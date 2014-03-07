import sys, urllib2, urllib, json

class bioresourcesdb_base(object):
    def studies(self):
        return [i[1] for i in self.rql('Any S,N  WHERE S is Study, S name N')]



class bioresourcesdb_HTTP(bioresourcesdb_base):
    url = 'http://is222241.intra.cea.fr:8080'

    def __init__(self, login=None, password=None, url=None):
        if url is not None:
            self.url = url
        if login:
            self.login(login, password)
            
    def login( self, login=None, password=None ):
        self.opener = urllib2.build_opener( urllib2.HTTPCookieProcessor() )
        values = {
            '__login': login,
            '__password': password,
            }
        self.opener.open( self.url, urllib.urlencode( values ) )

    def entities(self, entity_type):
        return json.load(self.opener.open( 
                    '%s/%s?vid=ejsonexport' % (self.url, entity_type)))

    def rql( self, rql, data=None ):
        if data is not None:
            rql = rql % data
        values = {
            'rql': rql,
            'vid': 'jsonexport',
            }
        return json.load( self.opener.open( self.url, urllib.urlencode( values ) ) )


BioresourcesDB = bioresourcesdb_HTTP()
