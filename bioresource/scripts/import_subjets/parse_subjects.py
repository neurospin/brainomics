# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 09:13:32 2014

@author: jl237561
"""

import os, csv, glob, sys

############################################################################
### Tools ##################################################################
############################################################################

def create_entity_safe(entity_name, **entity):
    db_entity = None
    res = session.find_entities(entity_name, **entity)
    is_existe = False
    for i in res:
        is_existe = True
        db_entity = i
        break
    if not is_existe:
        db_entity = session.create_entity(entity_name, **entity)
    return db_entity


def find_files(search_path, ext):
    result = [os.path.join(dp, f) \
                for dp, dn, filenames in os.walk(search_path) \
                for f in filenames \
                if os.path.splitext(f)[1] == ext]
    return result

############################################################################
### Subjects ###############################################################
############################################################################

def get_subjects_fam(filename):
    # filename = "/neurospin/brainomics/2014_bioresource/data/"\
    #            "genomic_platform_measure/illumina_610quad_data/"\
    #            "qc_subjects_qc_genetics_all_snps_wave1/"\
    #            "qc_subjects_qc_genetics_all_snps_wave1.fam"
    gender_map = {}
    gender_map["1"] = "male"
    gender_map["2"] = "female"
    subjects = []
    with open(filename) as infile:
        for line in infile:
            subject = dict()
            words = line.split(" ")
            subject["identifier"] = unicode(words[0])
            gender_code = words[4]
            if gender_code in gender_map:
                subject["gender"] = unicode(gender_map[gender_code])
            else:
                subject["gender"] = u"unknown"
            subject["handedness"] = u"unknown"
            subjects.append(subject)
    return subjects


def get_subjects_fams(filename):
    subjects = []
    res = find_files(filename, ".fam")
    for item in res:
        sub_subjects = get_subjects_fam(item)
        subjects += sub_subjects
    return subjects


def import_subjects(genomic_platform_measure_path):
    subjects = get_subjects_fams(genomic_platform_measure_path)
    db_subjects = []
    for subject in subjects:
        db_subject = create_entity_safe("Subject", **subject)
        db_subjects.append(db_subject)
    return db_subjects


def get_map_subjet_filename(filename):
    map_subjet_filename = {}
    res = find_files(filename, ".fam")
    for item in res:
        sub_subjects = get_subjects_fam(item)
        for sub_subject in sub_subjects:
            map_subjet_filename[sub_subject["identifier"]] = item
    return map_subjet_filename

############################################################################
### Centers ################################################################
############################################################################


def get_cng_center():
    center = {}
    center["identifier"] = u"CNG"
    center["name"] = u"CNG"
    center["department"] = u"Essonne"
    center["city"] = u"Evry"
    center["country"] = u"France"
    return center


def import_center():
    center = get_cng_center()
    db_center = create_entity_safe("Center", **center)
    return db_center

############################################################################
### GenomicPlatform ########################################################
############################################################################


def get_genomic_platform():
    platforms = []
    platform = {}
    platform["name"] = "Affymetrix_6.0"
    platforms.append(platform)
    platform = {}
    platform["name"] = "Illu_660"
    platforms.append(platform)
    platform = {}
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

############################################################################
### Assessment #############################################################
############################################################################


def get_cng_center_assesements(genomic_measures):
    assesements = []
    for genomic_measure in genomic_measures:
        assessment = {}
        assessment["identifier"] = genomic_measure[0]["identifier"]
        item = (assessment, genomic_measure)
        assesements.append(item)
    return assesements


############################################################################
### GenomicMeasure #########################################################
############################################################################


def get_genomic_measures(genomic_platform_measure_path):
    result = find_files(genomic_platform_measure_path, ".bed")
    measures = []
    for item_res in result:
        filepath = os.path.splitext(item_res)[0]
        filename = filepath.split("/")
        filename = filename[len(filename) - 1]
        measure = {}
        measure["identifier"] = unicode(filename)
        measure["filepath"] = unicode(filepath)
        measure["type"] = u"snps"
        measure["format"] = u"plink"
        measures.append(measure)
    return measures


def import_genomic_measures(genomic_platform_measure_path):
    db_genomic_measures = []
    genomic_measures = get_genomic_measures(genomic_platform_measure_path)
    for genomic_measure in genomic_measures:
        db_genomic_measure = create_entity_safe("GenomicMeasure",
                                                **genomic_measure)
        db_genomic_measures.append(db_genomic_measure)
    return db_genomic_measures


############################################################################
### SubjectGroup ###########################################################
############################################################################


def get_subject_groups(genomic_measures):
    subject_groups = []
    for genomic_measure in genomic_measures:
        subject_group = {}
        subject_group["identifier"] = genomic_measure["identifier"]
        subject_group["name"] = genomic_measure["identifier"]
        subject_groups.append(subject_group)
    return subject_groups


def import_subject_groups(genomic_measures):
    db_subject_groups = []
    subject_groups = get_subject_groups(genomic_measures)
    for subject_group in subject_groups:
        db_subject_group = create_entity_safe("SubjectGroup",
                                              **subject_group)
        db_subject_groups.append(db_subject_group)
    return db_subject_groups

############################################################################
### Relations ##############################################################
############################################################################


def import_rel_related_groups_4_subject_and_subject_groups(
        db_subjects,
        db_subject_groups,
        map_s_sg):
            pass


if __name__ == "__main__":
    root_path = "/neurospin/brainomics/2014_bioresource"
    genomic_platform_measure_path = os.path.join(
                                       root_path,
                                       "data",
                                       "genomic_platform_measure")
    genomic_measures = get_genomic_measures(genomic_platform_measure_path)
    db_subject_groups = import_subject_groups(genomic_measures)
    db_subjects = import_subjects(genomic_platform_measure_path)
    map_subjet_filename = \
            get_map_subjet_filename(genomic_platform_measure_path)
    session.commit()

#    res = {"identifier": u"data", "name": u"data"}
#    session.create_entity("SubjectGroup", **res)
#    res = {'format': u'Illu_610',
#           'identifier': u'qc_subjects_qc_genetics_all_snps_wave1',
#           'type': u'snps',
#           'filepath': u'/neurospin/brainomics/2014_bioresource/data/genomic_platform_measure/illumina_610quad_data/qc_subjects_qc_genetics_all_snps_wave1/qc_subjects_qc_genetics_all_snps_wave1'}
#    session.create_entity("GenomicMeasure", **res)
    # genomic_measures = get_genomic_measures(root_path)
    # assesements = get_cng_center_assesements(genomic_measures)
