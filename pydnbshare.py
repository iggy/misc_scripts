#!/usr/bin/python
# -*- coding: utf-8 -*-

# script to download releases from the dnbshare feed

# TODO it currently reads the entire mp3 into memory instead of writing
# it out to disk as it gets it
# what happens if the script dies?
# progress meter?

URL="http://www.dnbshare.com/feed"

import urllib2, re, httplib, urllib, os.path
from xml.dom.minidom import parse
from pprint import pprint

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
  
  #data = 'file=%s&payload=%s' % (mp3[rslash:], payload)
  data = urllib.urlencode({'file': mp3[rslash:], 'payload': payload})
  
  #print "posting to: ", url, data
  
  headers = {"Content-type": "application/x-www-form-urlencoded",'Referer': url}
  
  conn = httplib.HTTPConnection("dnbshare.com")
  
  conn.request('POST', url.replace('http://dnbshare.com',''), data, headers)
  resp = conn.getresponse()

  #pprint(resp.getheaders)
  mp3url = resp.getheader('Location')

  conn.close()

  out = open(mp3[rslash:], 'w+')
  mp3f = urllib2.urlopen(mp3url)
  out.write(mp3f.read())

#post = urllib2.urlopen(url, data)
  
  #print post.geturl()
  #out = open('tmp', 'w+')
  #out.write(post.read())
  
  #break
