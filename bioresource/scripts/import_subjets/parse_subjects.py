# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 09:13:32 2014

@author: jl237561
"""

import os, csv, glob, sys

def parse_subjets_fam_file(filename):
    # filename = "/neurospin/brainomics/2014_bioresource/data/genomic_platform_measure/Illu_610_data/qc_subjects_qc_genetics_all_snps_wave1/qc_subjects_qc_genetics_all_snps_wave1.fam"
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


def get_cng_center():
    center = {}
    center["entity_name"] = "Center"
    center["identifier"] = "CNG"
    center["name"] = "CNG"
    center["department"] = "Essonne"
    center["city"] = "Evry"
    center["country"] = "France"
    return center


def get_genomic_platform():
    platforms = []
    platform = {}
    platform["entity_name"] = "GenomicPlatform"
    platform["name"] = "Affymetrix_6.0"
    platforms.append(platform)
    platform = {}
    platform["entity_name"] = "GenomicPlatform"
    platform["name"] = "Illu_660"
    platforms.append(platform)
    platform = {}
    platform["entity_name"] = "GenomicPlatform"
    platform["name"] = "Illu_610"
    platforms.append(platform)
    return platforms


def get_platform_from_name(platforms, name):
    for platform in platforms:
        if name in platform["name"] or name == platform["name"]:
            return platform
    return None


def select_platform_from_filepath(filepath):
    platforms = get_genomic_platform()
    if "illumina_610quad" in filepath:
        return get_platform_from_name(platforms, "Illu_610")
    elif "illumina_660w" in filepath:
        return get_platform_from_name(platforms, "Illu_660")
    return None


def find_files(search_path, ext):
    result = [os.path.join(dp, f) \
                for dp, dn, filenames in os.walk(search_path) \
                for f in filenames \
                if os.path.splitext(f)[1] == ext]
    return result


def get_cng_center_assesement_genomic_measures(root_path):
    search_path = os.path.join(root_path,
                               "data",
                               "genomic_platform_measure")
    result = find_files(search_path, ".bed")
    platforms = get_genomic_platform()
    measures = []
    for item_res in result:
        filepath = os.path.splitext(item_res)[0]
        filename = filepath.split("/")
        filename = filename[len(filename) - 1]
        measure = {}
        measure["entity_name"] = "GenomicMeasure"
        measure["identifier"] = filename
        measure["filepath"] = filepath
        platform = select_platform_from_filepath(filepath)
        item_platform = (platform, [])
        mitem = (measure, item_platform)
        measures.append(mitem)
    return measures


def get_cng_center_assesements(genomic_measures):
    assesements = []
    for genomic_measure in genomic_measures:
        assesement = {}
        assesement["entity_name"] = "Assessment"
        assesement["identifier"] = genomic_measure[0]["identifier"]
        item = (assesement, genomic_measure)
        assesements.append(item)
    return assesements


def parse_genomic_measure():
    pass


if __name__ == "__main__":
    root_path = "/neurospin/brainomics/2014_bioresource"
    genomic_measures = get_cng_center_assesement_genomic_measures(root_path)
    assesements = get_cng_center_assesements(genomic_measures)
    
