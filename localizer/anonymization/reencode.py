#!/usr/bin/python
# -*- coding: utf-8 -*- 

import random
from itertools import izip

def random_conversion_table(subjects):
    """Return a random conversion table for re-encoding subject identifiers

    Arguments:
    subjects -- list of subject identifiers to re-encode

    Returns a subject -> code dictionary"""
    # number of subjects
    n = len(subjects)
    # create unique random integer identifiers
    array = range(1, n+1)
    random.shuffle(array)
    # create a unique string identifier based on the above integer identifier
    digits = len(str(n))
    return { subject: 'S' + str(code).zfill(digits) for subject, code in izip(subjects, array) }


import csv

def write_conversion_table(outfile, table):
    """Print conversion table to a CSV outfile

    Conversion table is a subject -> code dictionary
    """
    writer = csv.writer(outfile, delimiter=',')
    for item in table.items():
        writer.writerow(item)


def read_conversion_table(infile):
    """Read conversion table from infile

    The expected format of infile is one line per subject.
    The format of infile is CSV, each line looks like:
        subject,code

    Returns a subject -> code dictionary
    """
    reader = csv.reader(infile, delimiter=',')
    return { row[0].strip(): row[1].strip() for row in reader }


if __name__ == '__main__':

    import getopt
    import sys

    # parse command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hi:o:',
                                   ['help', 'input=', 'output='])
    except getopt.GetoptError as e:
        print >> sys.stderr, str(e)
        # TODO: print usage
        sys.exit(2)
    read_conversion_file = None
    write_conversion_file = None
    for o, a in opts:
        if o in ("-h", "--help"):
            # TODO: print usage
            sys.exit(0)
        elif o in ("-i", "--input"):
            read_conversion_file = a
        elif o in ("-o", "--output"):
            write_conversion_file = a
    if len(args) != 1:
        # TODO: print usage
        sys.exit(2)
    data_dir = args[0]

    import os.path

    # prepare to iterate over subject subdirectories in the subjects directory
    subjects_dir = os.path.join(data_dir, 'subjects')
    subjects = os.listdir(subjects_dir)

    genetics_dir = os.path.join(data_dir, 'genetics')

    # read or create subjects conversion table
    if read_conversion_file:
        with open(read_conversion_file, 'r') as infile:
            conversion_table = read_conversion_table(infile)
            conversion_set = set(conversion_table.keys())
            for subject in subjects:
                if subject not in conversion_set:
                    print >> sys.stderr, 'subject "%s" missing from conversion table' % subject
                    sys.exit(1)
    else:
        conversion_table = random_conversion_table(subjects)

    from tempfile import NamedTemporaryFile
    import shutil

   # re-encode genotypic data (FAM files only)
    for plink in os.listdir(genetics_dir):
        extension = os.path.splitext(plink)[1]
        if extension.upper() != '.FAM':
            continue
        with NamedTemporaryFile(delete=False) as tmpfile:
            with open(os.path.join(genetics_dir, plink)) as infile:
                for line in infile:
                    for subject, code in conversion_table.iteritems():
                        line = line.replace(subject, code)
                    tmpfile.write(line)
        shutil.move(tmpfile.name, infile.name)

    import json
    import re

    # re-encode subject data
    for subject in subjects:
        subject_dir = os.path.join(subjects_dir, subject)
        code = conversion_table[subject]
        encoded_dir = os.path.join(subjects_dir, code)

        # re-encode contents of behavioural.json
        with NamedTemporaryFile(delete=False) as tmpfile:
            behavioural_json = os.path.join(subject_dir, 'behavioural.json')
            with open(behavioural_json) as infile:
                contents = json.load(infile)
                contents['nip'] = contents['nip'].replace(subject, code)
            json.dump(contents, tmpfile, sort_keys=True)
        shutil.move(tmpfile.name, infile.name)

        # re-encode contents of spm.json
        # totally erase paths starting with /neurospin/unicog
        with NamedTemporaryFile(delete=False) as tmpfile:
            spm_json = os.path.join(subject_dir, 'spm.json')
            with open(spm_json) as infile:
                contents = json.load(infile)
                contents['c_maps'] = { key: '' for key in contents['c_maps'].keys() }
                contents['c_maps_smoothed'] = { key: '' for key in contents['c_maps_smoothed'].keys() }
                contents['data'] = [ '' for x in contents['data'] ]
                contents['mask'] = ''
                contents['raw_data'] = [ '' for x in contents['raw_data'] ]
                contents['subject'] = contents['subject'].replace(subject, code)
                contents['t_maps'] = { key: '' for key in contents['t_maps'].keys() }
            json.dump(contents, tmpfile, sort_keys=True)
        shutil.move(tmpfile.name, infile.name)

        # re-encode contents of subject.json
        with NamedTemporaryFile(delete=False) as tmpfile:
            subject_json = os.path.join(subject_dir, 'subject.json')
            with open(subject_json) as infile:
                contents = json.load(infile)
                # comments are tricky: they may reference other subjects
                if 'comments' in contents:
                    comments = contents['comments']
                    if comments:
                        for s, c in conversion_table.iteritems():
                            comments = comments.replace(s, c)
                        comments = re.sub('(bru\d{4})', '<sanitized>', comments)
                        contents['comments'] = comments
                # exam identifier may be different from subject identifier
                # discard it in case it starts with 'bru'
                contents['exam'] = contents['exam'].replace(subject, code)
                if contents['exam'].startswith('bru'):
                    contents['exam'] = '<sanitized>'
                contents['nip'] = contents['nip'].replace(subject, code)
            json.dump(contents, tmpfile, sort_keys=True)
        shutil.move(tmpfile.name, infile.name)

        # re-encode subject subdirectory name
        shutil.move(subject_dir, encoded_dir)

        # this directory may contain subject identifiers
        sprintBack = os.path.join(genetics_dir, 'sprintBack')
        if os.path.isdir(sprintBack):
            shutil.rmtree(sprintBack)

        # chmod -x
        # this has nothing to do with anonymization but I like to beautify!
        for root, dirs, files in os.walk(data_dir):  
            for name in files:
                os.chmod(os.path.join(root, name), 0o644)

    # write subjects conversion table
    if write_conversion_file:
        with open(write_conversion_file, 'w') as outfile:
            write_conversion_table(outfile, conversion_table)
