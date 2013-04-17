#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This script:
# * retrieves a list of all subjects from the Imagen XNAT database,
# * for each of the above subjects, dumps imaging and questionnaire
#   metadata into XML files
#
# See "XNAT REST API Directory" for details on XNAT REST queries
#     https://wiki.xnat.org/display/XNAT/XNAT+REST+API+Directory
#

#
# Imagen XNAT database
#
REST_URL = 'https://imagen.cea.fr/imagen_database/REST'
PROJECT = 'IMAGEN'

#
# logging
#
import logging
logging.root.setLevel(logging.INFO)

#
# connection to the XNAT server
#
# This class contains whatever is need for the connection, including an Http
# instance from httplib2.
#
from httplib2 import Http

class XNAT(object):
    def __init__(self, rest_url, project, name, password):
        rest_url = rest_url.rstrip('/')
        self._url = '{0}/projects/{1}'.format(rest_url, project)
        self._name = name
        self._password = password
        self._http = Http(disable_ssl_certificate_validation=True)
        self._http.add_credentials(self._name, self._password)

    def get(self, query, format):
        query = query.lstrip('/')
        uri = '{0}/{1}?format={2}'.format(self._url, query, format)
        return self._http.request(uri, 'GET')

#
# one XNAT instance per process
#
# This variable is initialized once in every process by the initialize().
#
_xnat = None

#
# process initilization
#
# This function initializes whatever has to be initialized in every process,
# including the main process. Currently only the above _xnat global variable
# needs be initialized.
#
def initialize(rest_url, project, name, password):
    global _xnat
    _xnat = XNAT(rest_url, project, name, password)

#
# worker function passed to child processes
#
# Retrieve metadata pertaining to subject as an XML file.
#
# Function intialize() muse be called prior to this function. Indeed the
# the _xnat global variable must be initialized before worker() is called.
#
import os

def worker(subject):
    status = None
    filename = subject + '.xml'
    if not os.path.exists(filename):
        query = 'subjects/{0}'.format(subject)
        try:
            global _xnat
            response, content = _xnat.get(query, 'xml')
            xml = open(filename, 'w')
            xml.write(content)
            xml.close()
            logging.info("Subject {0}: dumped to XML file {1}".format(subject, filename))
        except IOError as e:
            status = e.errno
            logging.error("Subject {0}: {1}: {2}".format(subject, filename, e.strerror))
        except httplib.HTTPException as e:
            status = e
            logging.error("Subject {0}: {1}".format(subject, str(e)))
            try:
                os.remove(filename)
            except OSError, e:
                pass
    return (subject, status)

#
# start the main process
#
# Notes:
# * Call initialize() before using _xnat in this main process.
# * Start child processes using Pool.multiprocessing. Functions initialize()
#   and worker() will be run in these child processes.
#
from getpass import getpass
import csv
from multiprocessing import Pool

if __name__ == '__main__':

    name = None
    while not name:
        name = raw_input('User: ')
    password = None
    while not password:
        password = getpass()

    # initialize the main process (global variable _xnat)
    initialize(REST_URL, PROJECT, name, password)

    # ask the XNAT server for a list of subjects as a CSV file
    response, content = _xnat.get('subjects', 'csv')
    # first row of XNAT CSV files is a header
    content = content.splitlines()[1:]
    # first column of the subjects CSV file is the subject ID
    subjects = [row[0] for row in csv.reader(content)]

    # the PostgreSQL server imagen-bis has 4 cores
    # it barely supports 8 processes when idle
    # use 6 of them to be on the safe side
    pool = Pool(6, initialize, (REST_URL, PROJECT, name, password))
    results = pool.map(worker, subjects)
    pool.close()
    pool.join()
