#!/usr/bin/python
# -*- coding: utf-8 -*-

SOURCE_DIR = '/neurospin/brainomics/2012_brainomics_localizer/data'

# create list of subjects
import os.path
subjects_dir = os.path.join(SOURCE_DIR, 'subjects')
subjects = os.listdir(subjects_dir)

# shuffle list of subjects
import random
random.shuffle(subjects)

# number of digits needed to express the largest list index
digits = len(str(len(subjects)))

# the new code is built from the randomly shuffled list index
i = 1
for subject in subjects:
    print subject + ',S' + str(i).zfill(digits)
    i += 1
