#!/usr/bin/env python3
#
# Copyright (c) 2011 David Johansen <david@makewhatis.com>
# Copyright (c) 2013 Brian Jackson <bjackson@bubbleup.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# <http://www.opensource.org/licenses/mit-license.php>
#
# See also: https://github.com/makewhatis/dnsmadeeasy-python/
#
# TODO
# update to newer DME rest API (this one uses 1.2, 2.0 is out)
"""
Python wrapper for the dnsmadeeasy RESTful api
"""

import httplib2
import json
from time import strftime, gmtime
import hashlib
import hmac
from optparse import OptionParser

class dme:
    """
    Create dnsmadeeasy object
    """
    def __init__(self, apikey, secret):
        self.api = apikey
        self.secret = secret
        #self.baseurl = "http://api.sandbox.dnsmadeeasy.com/V1.2/"
        # use below url for real api access. above is sandbox.
        self.baseurl = "http://api.dnsmadeeasy.com/V1.2/"
    def _headers(self):
        rightnow = self._get_date()
        hashstring = self._create_hash(rightnow)
        headers = {'x-dnsme-apiKey' : self.api, 'x-dnsme-hmac' : hashstring, 'x-dnsme-requestDate' : rightnow, 'content-type' : 'application/json' }
        return headers
    
    def _get_date(self):
        return strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

    def _create_hash(self, rightnow):
        return hmac.new(self.secret.encode(), rightnow.encode(), hashlib.sha1).hexdigest()
    
    def _rest_connect(self, resource, method, data=""):
        http = httplib2.Http()
        print(data)
        response, content = http.request(self.baseurl + resource, method, body=data, headers=self._headers())
        if (response['status'] == "200" or  response['status'] == "201" ):
            if content:
                jsonresponse = json.loads(content.decode('utf-8'))
                return jsonresponse
            else:
                return response
        else:
            print(content)
            raise Exception("Error talking to dnsmadeeasy: " + response['status'])               

    ########################################################################
    #  /domains
    ########################################################################

    def list_domains(self):
        domains = []
        jsonresponse = self._rest_connect('domains', 'GET')
        for domain in jsonresponse['list']:
            domains.append(domain)
        return domains
    
    #!!!!! Following function deletes all of your domains. Use that with caution. Why anybody would need this, who knows.!!!!!!!
    
    def delete_domains(self):
        jsonresponse = self._rest_connect('domains', 'DELETE')
        return jsonresponse
 
    ########################################################################
    #  /domains/{domainName}
    ########################################################################

    def get_domain(self, domain):
        domain_info = []
        jsonresponse = self._rest_connect('domains/' + domain, 'GET' )
        for info in jsonresponse.items():
            domain_info.append(info)
        return domain_info
    
    def delete_domain(self, domain):
        jsonresponse = self._rest_connect('domains/' + domain, 'DELETE')
        return jsonresponse
    
    def add_domain(self, domain):
        jsonresponse = self._rest_connect('domains/' + domain, 'PUT')
        return jsonresponse
 
    ########################################################################
    #  /domains/{domainName}/records
    ########################################################################
  
    def get_records(self, domain):
        records = []
        jsonresponse = self._rest_connect('domains/' + domain + '/records', 'GET')
        for record in jsonresponse:
            records.append(record)
        return records
        
    def add_record(self, domain, data):
        jsonresponse = self._rest_connect('domains/' + domain + '/records', 'POST', data)
        return jsonresponse

    ########################################################################
    #  /domains/{domainName}/records/{recordId}
    ########################################################################
    
    def get_record_byid(self, domain, id):
        jsonresponse = self._rest_connect('domains/' + domain + '/records/' + id, 'GET')
        return jsonresponse
        
    def delete_record_byid(self, domain, id):
        response = self._rest_connect('domains/' + domain + '/records/' + id, 'DELETE')
        return response
    
    def update_record_byid(self, domain, id, data):
        response = self._rest_connect('domains/' + domain + '/records/' + id, 'PUT', data)
        return response


parser = OptionParser()
parser.add_option("-A", "--add-record", dest="add",
                  help="add a name record")
parser.add_option("-D", "--delete-record", dest="delete",
                  help="delete a name record")
parser.add_option("-I", "--ip-addr", dest="ipaddr",
                  help="IP address of the record")
parser.add_option("-T", "--ttl", dest="ttl", default=30,
                  help="IP address of the record")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
parser.add_option("-a", "--api-key", dest="api_key",
                  help="DME API key")
parser.add_option("-s", "--secret-key", dest="secret_key",
                  help="DME secret key")

(options, args) = parser.parse_args()

if not options.api_key and not options.secret_key:
    print("You must specify API and secret keys for DNS Made Easy")
    exit(1)

dns = dme(options.api_key, options.secret_key)

if options.add and options.ipaddr:
    print("\nAdd record to domain: \n")
    data =  json.dumps({
        "name":options.add,
        "type":"A",
        "data":options.ipaddr,
        "gtdLocation":"Default",
        "ttl":options.ttl
    }, separators=(',', ':'))    
    result = dns.add_record('busites.com', data)
    print(result) 

if options.delete and options.ipaddr:
    rid = False
    
    print("\nDelete record from domain: \n")
    result = dns.get_records('busites.com')
    for x in result:
        if x['name'] == options.delete and x['data'] == options.ipaddr:
            rid = str(x['id'])
            
    if rid:
        result = dns.delete_record_byid('busites.com', rid)
    
        print(result)
    else:
        print("No record found to delete")
        exit(1)
