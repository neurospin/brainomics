#!/usr/bin/python
# -*- coding: utf-8 -*- 


DATA_DIR = '/volatile/2012_brainomics_localizer/data'


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


INFILE = '/home/dp165978/WORK_IN_PROGRESS/Localizer94/reencode.csv'

if __name__ == '__main__':

    import os.path

    # prepare to iterate over subject subdirectories in the subjects directory
    SUBJECTS_DIR = os.path.join(DATA_DIR, 'subjects')
    subjects = os.listdir(SUBJECTS_DIR)

    GENETICS_DIR = os.path.join(DATA_DIR, 'genetics')

    import sys

    # read or create subjects conversion table
    if INFILE:
        infile = open(INFILE, 'r')
        conversion_table = read_conversion_table(infile)
        conversion_set = set(conversion_table.keys())
        for subject in subjects:
            if subject not in conversion_set:
                print >> sys.stderr, 'subject "%s" missing from conversion table' % subject
                sys.exit()
    else:
        conversion_table = random_conversion_table(subjects)
        write_conversion_table(sys.stdout, conversion_table)

    from tempfile import NamedTemporaryFile
    import shutil

   # re-encode genotypic data (FAM files only)
    for plink in os.listdir(GENETICS_DIR):
        extension = os.path.splitext(plink)[1]
        if extension.upper() != '.FAM':
            continue
        with NamedTemporaryFile(delete=False) as tmpfile:
            with open(os.path.join(GENETICS_DIR, plink)) as infile:
                for line in infile:
                    for subject, code in conversion_table.iteritems():
                        line = line.replace(subject, code)
                    tmpfile.write(line)
        shutil.move(tmpfile.name, infile.name)

    import json

    # re-encode subject data
    for subject in subjects:
        code = conversion_table[subject]

        # re-encode contents of behavioural.json
        with NamedTemporaryFile(delete=False) as tmpfile:
            behavioural_json = os.path.join(SUBJECTS_DIR, subject, 'behavioural.json')
            with open(behavioural_json) as infile:
                contents = json.load(infile)
                contents['exam'] = contents['exam'].replace(subject, code)
                contents['nip'] = contents['nip'].replace(subject, code)
            json.dump(contents, tmpfile, sort_keys=True)
        shutil.move(tmpfile.name, infile.name)

        # re-encode contents of spm.json
        # totally erase paths starting with /neurospin/unicog
        with NamedTemporaryFile(delete=False) as tmpfile:
            spm_json = os.path.join(SUBJECTS_DIR, subject, 'spm.json')
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
            subject_json = os.path.join(SUBJECTS_DIR, subject, 'subject.json')
            with open(subject_json) as infile:
                contents = json.load(infile)
                # comments are tricky: the reference other subjects
                comments = contents['comments']
                for s, c in conversion_table.iteritems():
                    comments = comments.replace(s, c)
                contents['comments'] = comments
                contents['exam'] = contents['exam'].replace(subject, code)
                contents['nip'] = contents['nip'].replace(subject, code)
            json.dump(contents, tmpfile, sort_keys=True)
        shutil.move(tmpfile.name, infile.name)

        # re-encode subject subdirectory name
        shutil.move(os.path.join(SUBJECTS_DIR, subject), os.path.join(SUBJECTS_DIR, code))

        # a script in sprintBack contains subject identifiers
        shutil.rmtree(os.path.join(GENETICS_DIR, 'sprintBack'))

        # chmod -x
        for root, dirs, files in os.walk(DATA_DIR):  
            for name in files:
                os.chmod(os.path.join(root, name), 0o644)
