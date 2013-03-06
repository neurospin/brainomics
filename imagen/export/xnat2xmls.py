#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This script:
# * retrieves a list of all subjects from the Imagen XNAT database,
# * for each of the above subjects, dump imaging and questionnaire
#   metadata into XML files
#

import httplib2

xnat_rest_url = 'https://imagen.cea.fr/imagen_database/REST'
project = 'IMAGEN'


class XNATConnection( object ):
  def __init__( self, rest_url, login, password, project ):
    self.url = rest_url.rstrip('/') + '/projects/' + project
    self.http = httplib2.Http()
    self.http.add_credentials( login, password )

  def get_csv( self, relative_url ):
    url = self.url + '/' + relative_url.lstrip('/')
    resp, content = self.http.request( url + '?format=csv', 'GET' )
    result = [ [self.string_to_python(j) for j in i.split(',')] for i in content.strip().split( '\n' ) 
]
    header = result[ 0 ]
    values = result[ 1: ]
    return header, values

  def get_xml( self, relative_url ):
    url = self.url + '/' + relative_url.lstrip('/')
    resp, content = self.http.request( url + '?format=xml', 'GET' )
    return content

  @staticmethod
  def string_to_python( x ):
    if x != '':
      try:
        return eval( x )
      except SyntaxError:
        return x
    return  ''


if __name__ == '__main__':
  import sys, os, traceback
  from getpass import getpass, getuser
  
  xmls_directory = sys.argv[ 1 ]
  if not os.path.exists( xmls_directory ):
    os.mkdir( xmls_directory )
  
  default_user = getuser()
  print 'User [' + default_user + ']:',
  user = sys.stdin.readline().strip()
  if not user:
    user = default_user
  password = getpass()
  
  xnat = XNATConnection( xnat_rest_url, user, password, project )

  header, values = xnat.get_csv( 'subjects' )
  #print 'header:', header
  for subject in values:
    subject_id = subject[ 0 ]
    xml_file = os.path.join( xmls_directory, subject_id + '.xml' )
    error_file = os.path.join( xmls_directory, subject_id + '.error' )
    if not os.path.exists( xml_file ) and not os.path.exists( error_file ):
      print 'Retrieving subject', subject_id
      try:
        xml = xnat.get_xml( 'subjects/' + subject_id )
      except:
        traceback.print_exc()
        traceback.print_exc( file=open( error_file, 'w' ) )
      else:
        open( xml_file, 'w' ).write( xml )
        if os.path.exists( error_file ):
          os.remove( error_file )
    else:
      print 'Skipping subject', subject_id
    #header, values = xnat.get( 'subjects/' + subject[ 0 ] + '/experiments' )
    #for experiment in values:
      #print '  EXPERIMENT:', experiment[ 5 ], '(' + experiment[1] + ')'
      #header, values = xnat.get( 'experiments/' + experiment[ 1 ] + '/scans' )
      #for scan in values:
        #print '  SCAN:', scan
