#!/usr/bin/python
# -*- coding: utf-8 -*-

SOURCE_DIR = '/neurospin/brainomics/2012_brainomics_localizer/data'

subjects = []

import os.path
subjects_dir = os.path.join(SOURCE_DIR, 'subjects')
for subject in os.listdir(subjects_dir):
    subjects.append(subject)

# shuffle subjects
import random
shuffled = random.sample(subjects, len(subjects))

# number of digits needed to express the largest 'subjects' index
digits = 0
n = len(subjects)
while n:
    n /= 10  # base 10
    digits += 1

# print shuffled subjects and their new code
# the new code is simply built from the shuffled index
i = 0
for subject in shuffled:
    print subject + ', S' + str(i).zfill(digits)
    i += 1
