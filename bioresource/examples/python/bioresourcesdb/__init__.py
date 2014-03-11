# -*- coding: utf-8 -*-

import sys
import urllib2
import urllib
import json


class bioresourcedb_base(object):
    def studies(self):
        return [i[1] for i in self.rql('Any S,N  WHERE S is Study, S name N')]


class bioresourcesdb_HTTP(bioresourcedb_base):
    _BIORESOURCE_DB_URL = 'http://is222241.intra.cea.fr:8080'
    _EXPORT_TYPE = 'json'

    def __init__(self, login=None, password=None, url=None):
        if url is not None:
            self.url = url
        else:
            self.url = _BIORESOURCE_DB_URL
        if login:
            self.login(login, password)
            
    def login(self, login, password):
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        data = {
            '__login': login,
            '__password': password,
        }
        self.opener.open(self.url, urllib.urlencode(data))

    def entities(self, entity_type):
        data = {
            'vid': 'e' + _EXPORT_TYPE + 'export',
        }
        return json.load(self.opener.open(self.url + '/' + entity_type,
                                           urllib.urlencode(data)))

    def rql(self, rql, data=None):
        if data is not None:
            rql %= data
        data = {
            'rql': rql,
            'vid': _EXPORT_TYPE + 'export',
        }
        return json.load(self.opener.open(self.url, urllib.urlencode(data)))


BioresourcesDB = bioresourcesdb_HTTP()
