#!/usr/bin/python3

# Fetch recent torrents from a certain site

# login, fetch rss feed (or screen scrape since rss feed never works), fetch recent torrents

# ~/.gt/config.ini format (the following 3 lines without leading "# "):
# [gettorrents]
# user=foo
# password=ouisfoi432589f
#
# run it in a script that copies the resulting torrent files to your torrent blackhole
#

import requests, re, os.path, urllib, configparser, sys

CFGFILE = os.path.expanduser('~/.gt/config.ini')

cfg = configparser.ConfigParser()
try:
    cfg.read(CFGFILE)
    USER = cfg['gettorrents']['user']
    PASS = cfg['gettorrents']['password']

except:
    print('Failed to read ' + CFGFILE)
    sys.exit(1)

s = requests.Session()
login = s.post('https://gettorrents.org/takelogin.php', data={'username':USER, 'password':PASS, 'logout':'no', })

for page in range(3):
    print('Fetching page: ', page)
    resp = s.get('https://gettorrents.org/browse.php?incldead=0&c27=1&page=' + str(page))

    x = re.findall(b'download.php/[^"]+', resp.content)

    for i in x:
        filename = u'fetched/' + str(urllib.request.unquote(i.decode('UTF-8').split('/')[-1]).encode('ascii', 'ignore'))
        #filename = tr.headers['content-disposition'].split('"')[1]


        if not os.path.isfile(filename):
            tr = s.get('https://gettorrents.org/' + i.decode('UTF-8'))
            print('saving torrent to: ', filename)
            f = open(filename, 'wb')
            f.write(tr.content)
            f.close()
