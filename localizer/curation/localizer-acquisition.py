#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Print PIN and series date for all MRI acquisitions that
# contain a localizer sequence. We expect localizer sequences
# to live in directories containing the "localizer" string.
#

# paths to Neurospin MRI data
path_3T = '/neurospin/acquisition/database/TrioTim'
path_7T = '/neurospin/acquisition/database/Investigational_Device_7T'

import re

# name of path to MRI data is expected to follow some rules
pattern_date = re.compile('^(\d{4})(\d{2})(\d{2})$')
pattern_patient = re.compile('^(\w{2}\d{6})-')
pattern_series = re.compile('localizer', re.IGNORECASE)

import os
import datetime

for path in (path_3T, path_7T):
    for date in os.listdir(path):
        match = pattern_date.match(date)
        if not match:
            continue
        date_path = os.path.join(path, date)
        if not os.path.isdir(date_path):
            continue
        y = int(match.group(1))
        m = int(match.group(2))
        d = int(match.group(3))
        for patient in os.listdir(date_path):
            match = pattern_patient.match(patient)
        if not match:
            continue
        patient_path = os.path.join(date_path, patient)
        if not os.path.isdir(patient_path):
            continue
        patient = match.group(1)
        for series in os.listdir(patient_path):
            match = pattern_series.search(series)
            if match:
                series_path = os.path.join(patient_path, series)
                if os.path.isdir(series_path):
                    relpath = os.path.join(date, patient, series)
                    print patient.upper(), datetime.date(y, m, d), relpath
                    break
