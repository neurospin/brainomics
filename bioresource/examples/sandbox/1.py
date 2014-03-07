#!/usr/bin/python

import urllib

request = 'Any G,B,E,SN WHERE G name "KIF1B", G start_position B, G stop_position E, S is Snp, S rs_id SN, S position SP HAVING SP > B, SP < E'
values = {
    'rql': request,
    'vid': 'csvexport',
}

print 'http://is222241.intra.cea.fr:8080/view?' + urllib.urlencode(values)
