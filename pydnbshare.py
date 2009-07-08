#!/usr/bin/python
# -*- coding: utf-8 -*-

# script to download releases from the dnbshare feed

# TODO 
# what happens if the script dies? loses connection? whatever?

URL="http://www.dnbshare.com/feed"

import urllib2, re, httplib, urllib, os.path, sys, math
from xml.dom.minidom import parse

fd = urllib2.urlopen(URL)

xml = parse(fd)

links = xml.getElementsByTagName('link')[1:]

for link in links:
    url = link.firstChild.data
    mp3 = url.replace('.html', '')
    rslash = mp3.rfind('/') + 1

    if os.path.exists(mp3[rslash:]):
        continue

    print url
    pg = urllib2.urlopen(url).read()

    payload = re.search('name="payload" value="([^"]*)', pg).group(1)

    data = urllib.urlencode({'file': mp3[rslash:], 'payload': payload})

    headers = {"Content-type": "application/x-www-form-urlencoded",'Referer': url}

    conn = httplib.HTTPConnection("dnbshare.com")

    conn.request('POST', url.replace('http://dnbshare.com',''), data, headers)
    resp = conn.getresponse()

    mp3url = resp.getheader('Location')

    conn.close()

    out = open(mp3[rslash:], 'w+')
    mp3f = urllib2.urlopen(mp3url)
    osize = float(mp3f.info().getheader('Content-Length'))

    #print "Size: %10s", mp3f.info().getheader('Content-Length')

    amountread = float(0)
    #print "  0%"
    while mp3f:
        data = mp3f.read(4096)
        if len(data) == 0:
            break
        amountread += len(data)
        pct = amountread / osize * 100
        sys.stdout.write("\r[T:%10d][R:%10d] %8d%%" % (osize, amountread, pct))
        sys.stdout.flush()
        out.write(data)

    print "\n"
    out.close()