#!/usr/bin/python
# -*- coding: utf-8 -*-

# reference list
PINS = 'LISTE_NIP.txt'

# path to JSON files - metadata extracted from the PostgreSQL database
SUBJECTS = '/neurospin/brainomics/2012_brainomics_localizer/localizer/subjects'

# metadata already extracted from GRR
GRR = 'localizer-grr.txt'

# metadata already extracted from /neurospin/acquisition
ACQUISITION = 'localizer-acquisition.txt'

import os
import sys
import json
import datetime
import MySQLdb

result = {}
# iterate over subjects in our reference list
pins_file = open(PINS, 'r')
for line in pins_file:
    # metadata from reference list
    pin, ref_aq = line.split()
    result[pin] = {'orig_ref_aq': ref_aq, }
    # where to find JSON files for each subject
    subject_path = os.path.join(SUBJECTS, pin)
    if not os.path.isdir(subject_path):
        print >> sys.stderr, 'ERROR: missing PIN directory:', pin
        continue
    # JSON metadata related to MRI inclusion?
    subject_file = open(os.path.join(subject_path, 'subject.json'), 'r')
    subject_data = json.load(subject_file)
    if 'date' in subject_data and subject_data['date']:
        inclusion_date = datetime.datetime.strptime(subject_data['date'], "%Y-%m-%d %H:%M:%S").date()
        result[pin]['json_inclusion_date'] = inclusion_date
    subject_file.close()
    # JSON metadata related to questionnaire?
    behavioural_file = open(os.path.join(subject_path, 'behavioural.json'), 'r')
    behavioural_data = json.load(behavioural_file)
    if 'date' in behavioural_data and behavioural_data['date']:
        questionnaire_date = datetime.datetime.strptime(behavioural_data['date'], "%Y-%m-%d %H:%M:%S").date()
        result[pin]['json_questionnaire_date'] = questionnaire_date
    behavioural_file.close()
pins_file.close()

acquisition = {}
# iterate over /neurospin/acquisition
# only keep PINs from our initial list
acquisition_file = open(ACQUISITION, 'r')
for line in acquisition_file:
    pin, date, rel_path = line.split()
    pin = pin.upper()
    if pin in result:
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        acquisition.setdefault(pin, {})[date] = rel_path
acquisition_file.close()

grr = {}
# iterate over GRR inclusions
# only keep PINs from our initial list
grr_file = open(GRR, 'r')
for line in grr_file:
    pin, date, ref_aq = line.split()
    pin = pin.upper()
    if pin in result:
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        grr.setdefault(pin, {})[date] = ref_aq
grr_file.close()

# try to match GRR inclusion dates
for pin in grr.keys():
    pin = pin.upper()
    date = None
    # first try to match JSON inclusion date
    if 'json_inclusion_date' in result[pin] and result[pin]['json_inclusion_date'] in grr[pin]:
        date = result[pin]['json_inclusion_date']
        result[pin]['date'] = date
        result[pin]['grr_ref_aq'] = grr[pin][date]
        if pin in acquisition and date in acquisition[pin]:
            result[pin]['rel_path'] = acquisition[pin][date]
    # alternatively try to match JSON questionnaire date
    elif 'json_questionnaire_date' in result[pin] and result[pin]['json_questionnaire_date'] in grr[pin]:
        date = result[pin]['json_questionnaire_date']
        result[pin]['date'] = date
        result[pin]['grr_ref_aq'] = grr[pin][date]
        if pin in acquisition and date in acquisition[pin]:
            result[pin]['rel_path'] = acquisition[pin][date]
    # finally try to match /neurospin/acquisition dates
    elif pin in acquisition:
        for date in sorted(acquisition[pin].keys(), reverse=True):
            if date in acquisition[pin]:
                result[pin]['date'] = date
                result[pin]['grr_ref_aq'] = grr[pin][date]
                result[pin]['rel_path'] = acquisition[pin][date]

print '========================================================================================================'
print 'PIN           JSON date of   JSON date of   retained date  retained CPP   original CPP   relative'
print '              inclusion      questionnaire                                               path'
print '========================================================================================================'
for pin, value in result.iteritems():
    if 'json_inclusion_date' in value:
        json_inclusion_date = value['json_inclusion_date']
    else:
        json_inclusion_date = None
    if 'json_questionnaire_date' in value:
        json_questionnaire_date = value['json_questionnaire_date']
    else:
        json_questionnaire_date = None
    if 'date' in value:
        date = value['date']
    else:
        date = None
    if 'grr_ref_aq' in value:
        grr_ref_aq = value['grr_ref_aq']
    else:
        grr_ref_aq = None
    if 'orig_ref_aq' in value:
        orig_ref_aq = value['orig_ref_aq']
    else:
        orig_ref_aq = None
    if 'rel_path' in value:
        rel_path = value['rel_path']
    else:
        rel_path = None
    print '%-8s      %-10s     %-10s     %-10s     %-10s     %-10s     %-10s' % (pin, str(json_inclusion_date), str(json_questionnaire_date), str(date), str(grr_ref_aq), str(orig_ref_aq), str(rel_path))
