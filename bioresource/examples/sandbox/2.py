#!/usr/bin/python

import urllib
import urllib2
import urlparse

request = 'Any G,B,E,SN WHERE G name "KIF1B", G start_position B, G stop_position E, S is Snp, S rs_id SN, S position SP HAVING SP > B, SP < E'
format = 'json'  # 'csv'
values = {
    'rql': request,
    'vid': format + 'export',
}

url = 'http://is222241.intra.cea.fr:8080/view?' + urllib.urlencode(values)

response = urllib2.urlopen(url)
data = response.read()

print data
