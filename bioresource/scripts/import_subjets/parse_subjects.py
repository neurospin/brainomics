# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 09:13:32 2014

@author: jl237561
"""


def parse_subjets_fam_file(filename):
    # filename = "/neurospin/brainomics/2014_bioresource/data/platforms/Illu_610_data/qc_subjects_qc_genetics_all_snps_wave1/qc_subjects_qc_genetics_all_snps_wave1.fam"
    gender_map = {}
    gender_map["1"] = "male"
    gender_map["2"] = "female"
    subjects = []
    with open(filename) as infile:
        for line in infile:
            subject = dict()
            subject["entity_name"] = "Subject"
            words = line.split(" ")
            subject["identifier"] = words[0]
            gender_code = words[4]
            if gender_code in gender_map:
                subject["gender"] = gender_map[gender_code]
            else:
                subject["gender"] = "unknown"
            subjects.append(subject)
    subjects.append([])


def get_centers():
    centers = []
    center = {}
    center["entity_name"] = "Center"
    center["identifier"] = "CNG"
    center["name"] = "CNG"
    center["department"] = "Essonne"
    center["city"] = "Evry"
    center["country"] = "France"
    centers.append(center)
    return centers


def get_genomic_platform():
    platforms = []
    platform = {}
    platform["entity_name"] = "GenomicPlatform"
    platform["name"] = "Affymetrix_6.0"
    platforms.append(platform)
    platform["entity_name"] = "GenomicPlatform"
    platform["name"] = "Illu_660"
    platforms.append(platform)
    platform["entity_name"] = "GenomicPlatform"
    platform["name"] = "Illu_610"
    platforms.append(platform)
    return platforms


def parse_genomic_measure():
    
