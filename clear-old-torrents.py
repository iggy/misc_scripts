#!/usr/bin/python3

# tunables/config
LDIR = '/dl/complete'
RDIR = '/stuff/tmp'
MINSPACE = '8G'
# Check to see if there is an rsync running and bail so we don't pull anything
# out from under any sync scripts
CHECKRSYNC = True

import argparse
import os
import string
import subprocess
import sys
from transmission import Transmission

try:
    rpid = subprocess.check_output(['pidof', 'rsync'])
except subprocess.CalledProcessError:
    # non-zero return... i.e. it's not running
    rpid = None

if CHECKRSYNC and rpid:
    sys.exit(0)

arg = argparse.ArgumentParser(description='Clean out old torrents to get below a configurable amount of space')
arg.add_argument('--pretend', '-p', const=True, nargs='?', help='Dont really do anything')
args = arg.parse_args()

ms = MINSPACE
if 'T' in ms or 't' in ms:
    ms = int(ms.strip(string.ascii_letters)) << 40
elif 'G' in ms or 'g' in ms:
    ms = int(ms.strip(string.ascii_letters)) << 30
elif 'M' in ms or 'm' in ms:
    ms = int(ms.strip(string.ascii_letters)) << 20
elif 'K' in ms or 'k' in ms:
    ms = int(ms.strip(string.ascii_letters)) << 10
ms = int(ms)

print('Removing old torrents until we have at least %d bytes free space' % ms)

t = Transmission(username='transmission', password='TafEcHadZid8')

resp = t('torrent-get', fields=['id', 'name','hashString', 'dateCreated', 'doneDate', 'sizeWhenDone', 'creator'])

resp['torrents'].sort(key=lambda item:item['dateCreated'])

for torrent in resp['torrents']:
    if not torrent['doneDate']:
         continue
    stat = os.statvfs(LDIR)
    if stat.f_bavail * stat.f_bsize < ms:
        if args.pretend:
            print('Pretending', torrent['name'].encode('UTF-8', errors='ignore'))
        
        else:
            print('Removing', torrent['name'].encode('UTF-8', errors='ignore'))
            t('torrent-remove', ids=[torrent['id']], delete_local_data=True)
