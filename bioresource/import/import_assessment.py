# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 09:13:32 2014

@author: jl237561
"""

import os, csv, glob, sys

############################################################################
### Constants ##############################################################
############################################################################

PLATFORM_AFFYMETRIX_6_0 = u"Affymetrix_6.0"
PLATFORM_ILLUMINA_610QUAD = u"Illumina_610"
PLATFORM_ILLUMINA_660W = u"Illumina_660"


############################################################################
### Tools ##################################################################
############################################################################


def get_filename_no_extension(filepath):
    '''
    Example
    -------
    >>> print get_filename_no_extension("/tmp/data.txt")
    data
    '''
    return os.path.basename(os.path.splitext(filepath)[0])


def get_filepath_no_extension(filepath):
    '''
    Example
    -------
    >>> print get_filepath_no_extension("/tmp/data.txt")
    /tmp/data
    '''
    return os.path.splitext(filepath)[0]


def create_entity_safe(entity_name, **entity):
    db_entity = None
    #Patch for Subject who should be uniquely identified by identifier
    res = []
    if entity_name == 'Subject':
        subject = dict()
        subject['identifier'] = entity['identifier']
        res = session.find_entities(entity_name, **subject)
    else:
        res = session.find_entities(entity_name, **entity)
    #End of patch
    is_existe = False
    for i in res:
        is_existe = True
        db_entity = i
        break
    if not is_existe:
        db_entity = session.create_entity(entity_name, **entity)
    return db_entity

def add_relation_safe(eid1,
                      rel_name,
                      eid2):
    rql = "Any X, Y where X eid %d, Y eid %d, X %s Y" % \
            (eid1, eid2, rel_name)
    rows = session.execute(rql)
    if rows.rowcount == 0:
        session.add_relation(eid1, rel_name, eid2)


def find_files(search_path, ext):
    result = [os.path.join(dp, f) \
                for dp, dn, filenames in os.walk(search_path) \
                for f in filenames \
                if os.path.splitext(f)[1] == ext]
    return result


def import_rel_one_vs_one2(list1, list2, attr_name, rel_name):
    # bijection
    import_rel_one_vs_one(list1,
                          attr_name,
                          list2,
                          attr_name,
                          rel_name)


def import_rel_one_vs_one(list1, attr_name1, list2, attr_name2, rel_name):
    # bijection
    for element1 in list1:
        for element2 in list2:
            if getattr(element1, attr_name1) == \
                getattr(element2, attr_name2):
                    eid1 = getattr(element1, "eid")
                    eid2 = getattr(element2, "eid")
                    add_relation_safe(eid1, rel_name, eid2)


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
            subject["identifier"] = unicode('IMAGEN_%s' % words[0])
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


def locate_db_subject(db_subjects, subject_name):
    for db_subject in db_subjects:
        if db_subject.identifier == subject_name:
            return db_subject
    return None

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


def get_genomic_platforms():
    platforms = []
    platform = {}
    platform["name"] = PLATFORM_AFFYMETRIX_6_0
    platforms.append(platform)
    platform = {}
    platform["name"] = PLATFORM_ILLUMINA_660W
    platforms.append(platform)
    platform = {}
    platform["name"] = PLATFORM_ILLUMINA_610QUAD
    platforms.append(platform)
    return platforms


def get_platform_from_name(platforms, name):
    for platform in platforms:
        if name in platform["name"] or name == platform["name"]:
            return platform
    return None


def get_db_platform_from_name(db_platforms, name):
    for db_platform in db_platforms:
        if name in db_platform.name or name == db_platform.name:
            return db_platform
    return None


def select_platform_from_filepath(filepath):
    platforms = get_genomic_platforms()
    if u"illumina_610quad" in filepath:
        return get_platform_from_name(platforms, PLATFORM_ILLUMINA_610QUAD)
    elif u"illumina_660w" in filepath:
        return get_platform_from_name(platforms, PLATFORM_ILLUMINA_660W)
    return None


def select_db_platform_from_filepath(filepath, db_platforms):
    if u"illumina_610quad" in filepath:
        return get_db_platform_from_name(db_platforms, PLATFORM_ILLUMINA_610QUAD)
    elif u"illumina_660w" in filepath:
        return get_db_platform_from_name(db_platforms, PLATFORM_ILLUMINA_660W)
    return None


def import_genomic_platforms():
    db_genomic_platforms = []
    genomic_platforms = get_genomic_platforms()
    for genomic_platform in genomic_platforms:
        db_genomic_platform = create_entity_safe("GenomicPlatform",
                                                **genomic_platform)
        db_genomic_platforms.append(db_genomic_platform)
    return db_genomic_platforms

############################################################################
### Assessment #############################################################
############################################################################


def locate_db_assessment(db_assessments, filename):
    for db_assessment in db_assessments:
        if db_assessment.identifier in filename:
            return db_assessment
    return None


def get_cng_center_assessments(genomic_measures):
    assessments = []
    for genomic_measure in genomic_measures:
        assessment = {}
        assessment["identifier"] = get_filename_no_extension(
                                        genomic_measure["filepath"])
        assessments.append(assessment)
    return assessments


def import_cng_center_assessments(genomic_measures):
    db_cng_center_assessments = []
    cng_center_assessments = get_cng_center_assessments(genomic_measures)
    for cng_center_assessment in cng_center_assessments:
        db_cng_center_assessment = create_entity_safe("Assessment",
                                        **cng_center_assessment)
        db_cng_center_assessments.append(db_cng_center_assessment)
    return db_cng_center_assessments


############################################################################
### GenomicMeasure #########################################################
############################################################################

def select_db_genomic_measure_from_filepath(
                                        db_genomic_measures,
                                        filepath):
    for db_genomic_measure in db_genomic_measures:
        if db_genomic_measure.filepath == filepath:
            return db_genomic_measure
    return None


def get_genomic_measures(all_fam_files):
    measures = []
    for item_res in all_fam_files:
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
    fam_files = find_files(genomic_platform_measure_path, ".fam")
    genomic_measures = get_genomic_measures(fam_files)
    for genomic_measure in genomic_measures:
        db_genomic_measure = create_entity_safe("GenomicMeasure",
                                                **genomic_measure)
        db_genomic_measures.append(db_genomic_measure)
    return db_genomic_measures


############################################################################
### Study ##################################################################
############################################################################


def get_studies(genomic_measures):
    studies = []
    for genomic_measure in genomic_measures:
        study = {}
        study["name"] = get_filename_no_extension(
                            genomic_measure["filepath"])
        study["data_filepath"] = u""
        studies.append(study)
    return studies


def import_studies(genomic_measures):
    study = {"name": u"GIMAGEN", "data_filepath": u""}
    db_study = create_entity_safe("Study",
                                   **study)
    db_studies = []
    db_studies.append(db_study)
    return db_studies

############################################################################
### Relations ##############################################################
############################################################################


def get_map_subjet_filename(all_fam_files):
    map_subject_name_2_filepath = {}
    for item in all_fam_files:
        sub_subjects = get_subjects_fam(item)
        for sub_subject in sub_subjects:
            map_subject_name_2_filepath[sub_subject["identifier"]] = item
    return map_subject_name_2_filepath


def import_rel_related_study_4_genomic_measures_and_studies(
                                    db_genomic_measures,
                                    db_studies
                                    ):
    for db_genomic_measure in db_genomic_measures:
        db_genomic_measure_name = get_filename_no_extension(
                                    db_genomic_measure.filepath)
        add_relation_safe(db_genomic_measure.eid,
                          "related_study",
                          db_studies[0].eid)


def import_rel_platform_4_genomic_measures_and_genomic_platform(
                                    db_genomic_measures,
                                    db_genomic_platforms
                                    ):
    for db_genomic_measure in db_genomic_measures:
        db_platform = select_db_platform_from_filepath(
                                db_genomic_measure.filepath,
                                db_genomic_platforms)
        add_relation_safe(db_genomic_measure.eid,
                          "platform",
                          db_platform.eid)


def import_rel_holds_4_assessments_and_center(
                                    db_center,
                                    db_assessments
                                    ):
    for db_assessment in db_assessments:
        add_relation_safe(db_center.eid,
                          "holds",
                          db_assessment.eid)


def import_rel_concerned_by_4_subject_and_assessments(
                                    db_subjects,
                                    db_assessments,
                                    map_subject_name_2_filepath):
    for subject_name in map_subject_name_2_filepath:
        db_subject = locate_db_subject(db_subjects,
                                       subject_name)
        db_assessment = locate_db_assessment(
                                db_assessments,
                                map_subject_name_2_filepath[subject_name])
        if (db_subject is not None) and (db_assessment is not None):
            add_relation_safe(db_subject.eid,
                              "concerned_by",
                              db_assessment.eid)


def import_rel_generates_4_assessments_and_genomic_measures(
                                    db_assessments,
                                    db_genomic_measures):
    for db_assessment in db_assessments:
        filename_no_extension = db_assessment.identifier
        for db_genomic_measure in db_genomic_measures:
            gm_filename_no_extension = get_filename_no_extension(
                                            db_genomic_measure.filepath)
            if filename_no_extension == gm_filename_no_extension:
                add_relation_safe(db_assessment.eid,
                                  "generates",
                                  db_genomic_measure.eid)


def import_rel_concerns_4_genomic_measure_and_subjects(
                                    db_genomic_measures,
                                    db_subjects,
                                    map_subject_name_2_filepath):
    for db_subject in db_subjects:
        filepath = map_subject_name_2_filepath[db_subject.identifier]
        file_path_no_extension = get_filepath_no_extension(filepath)
        db_genomic_measure = select_db_genomic_measure_from_filepath(
                                                db_genomic_measures,
                                                file_path_no_extension)
        if (db_subject is not None) and (db_genomic_measure is not None):
            add_relation_safe(db_genomic_measure.eid,
                              "concerns",
                              db_subject.eid)


def import_rel_related_study_4_assessment_and_study(
                                db_assessments,
                                db_studies):
    for db_assessment in db_assessments:
        add_relation_safe(db_assessment.eid,
                          "related_study",
                          db_studies[0].eid)

if __name__ == "__main__":
    root_path = "/neurospin/brainomics/2014_bioresource"
    genomic_platform_measure_path = os.path.join(
                                       root_path,
                                       "data",
                                       "genomic_platform_measure")
    all_fam_files = find_files(genomic_platform_measure_path,
                               ".fam")
    map_subject_name_2_filepath = get_map_subjet_filename(all_fam_files)
    genomic_measures = get_genomic_measures(all_fam_files)
    db_subjects = import_subjects(genomic_platform_measure_path)
    db_studies = import_studies(genomic_measures)
    db_genomic_measures = import_genomic_measures(
                            genomic_platform_measure_path)
    db_genomic_platforms = import_genomic_platforms()
    db_center = import_center()
    db_cng_center_assessments = import_cng_center_assessments(
                                    genomic_measures)
    import_rel_concerns_4_genomic_measure_and_subjects(
                db_genomic_measures,
                db_subjects,
                map_subject_name_2_filepath)
    import_rel_related_study_4_genomic_measures_and_studies(
                db_genomic_measures,
                db_studies)
    import_rel_related_study_4_assessment_and_study(
                db_cng_center_assessments,
                db_studies)
    import_rel_holds_4_assessments_and_center(
                db_center,
                db_cng_center_assessments)
    import_rel_concerned_by_4_subject_and_assessments(
                db_subjects,
                db_cng_center_assessments,
                map_subject_name_2_filepath)
    import_rel_platform_4_genomic_measures_and_genomic_platform(
                db_genomic_measures,
                db_genomic_platforms)
    import_rel_generates_4_assessments_and_genomic_measures(
                db_cng_center_assessments,
                db_genomic_measures)
    # add relation from genomic measure to subjects
    session.commit()

    """Import finished. Here you some rqls to test import
Any X, Y where X is Subject, Y is Assessment, X concerned_by Y
Any X, Y where X is Assessment, Y is GenomicMeasure, X generates Y
Any X, Y where X is Center, Y is Assessment, X holds Y
Any X, Y where X is GenomicMeasure, Y is GenomicPlatform, X platform Y
    """
