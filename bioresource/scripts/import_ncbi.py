# -*- coding: utf-8 -*-

import sys
import os
import os.path as osp
import re
import glob
import csv
import json
import pickle
from datetime import datetime
from hashlib import sha1
import csv
import datetime
import numpy as np
from bisect import bisect_left, bisect_right
from cubes.brainomics.importers.helpers import (get_image_info,
                                                import_genes,
                                                import_chromosomes,
                                                import_snps)

class compute_opt:
    snps = "SNPS"

def read_csv_col(filename, ncol, quote='"', spliter=","):
    """
    Example
    -------
    read_csv_col(path_genome_wide_snp_6_na33_annot,[0,1])[1:]
    """
    ncol = np.asarray(ncol)
    # Count line number
    n_lines = 0
    with open(filename) as infile:
        for line in infile:
            if line.strip()[0] == "#":
                continue
            n_lines = n_lines + 1
    # Count max string item length
    max_len = 0
    with open(filename) as infile:
        for line in infile:
            if line.strip()[0] == "#":
                continue
            cols = line.split(spliter)
            cols = np.asarray(cols)
            col_val = cols[ncol]
            for i in xrange(len(col_val)):
                col_val[i] = col_val[i].strip(quote)
                if max_len < len(col_val[i]):
                    max_len = len(col_val[i])
    # Create numpy string matrix
    col_vals = np.empty([n_lines, len(ncol)],
                         dtype="S%s" % max_len)
    # Fill numpy string matrx
    i_line = 0
    with open(filename) as infile:
        for line in infile:
            if line.strip()[0] == "#":
                continue
            cols = np.asarray(line.split(spliter))
            col_val = cols[ncol]
            for i in xrange(len(col_val)):
                col_vals[i_line, i] = col_val[i].strip(quote)
            i_line = i_line + 1
    return col_vals


def read_snps_human6xxw_quad_v1_h_bed(filename):
    # filename = "/volatile/jinpeng/frouin/ncbi/scripts/ncbi/platforms/human660w-quad_v1_h.bed"
    n_skip_lines = 1
    i_line = 0
    res_set = set()
    with open(filename) as infile:
        for line in infile:
            if i_line < n_skip_lines:
                i_line = i_line + 1
                continue
            i_line = i_line + 1
            words = line.split("\t")
            res_set.add(words[3].strip(" \n"))
    return res_set


def read_snps_rsid_genome_wide_snp_6_na33_annot(
                    path_genome_wide_snp_6_na33_annot,
                    pattern="(.*)"):
    import re
    res_set = read_csv_col(path_genome_wide_snp_6_na33_annot,[0,1])[1:]
    mask = np.array(len(res_set) * [False], bool)
    for i in xrange(len(res_set)):
        # i = 0
        one_res = res_set[i]
        if re.search(pattern, one_res[0]) is not None:
            mask[i] = True
    res_set = res_set[mask]
    snps_set = set(res_set[:, 1])
    del res_set
    return snps_set


def get_name_map_eid(session, entity_name, attribute_name):
    map_data = {}
    entities = session.find_entities(entity_name)
    for entity in entities:
        map_data[getattr(entity, attribute_name)] = entity.eid
    return map_data


def line_numbers(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def add_rel_platform_snp(store,
                         platform_eids,
                         platform_snps,
                         snp_rs_id,
                         snp_db):
    for platform_name in platform_eids:
        if snp_rs_id in platform_snps[platform_name]:
            # print "A new platform relation has been added."
            store.relate(platform_eids[platform_name],
                         'related_snps',
                         snp_db.eid)


def find_le(a, x):
    'Find rightmost value less than or equal to x'
    i = bisect_right(a, x)
    if i:
        return a[i-1]
    return None


def find_lt(a, x):
    'Find rightmost value less than x'
    i = bisect_left(a, x)
    if i:
        return a[i-1]
    raise ValueError


def get_sorted_genes_db(session):
    genes = session.find_entities("Gene")
    gene_list = []
    for gene in genes:
        data_element = (gene.eid,
                        gene.start_position,
                        gene.stop_position)
        gene_list.append(data_element)
    gene_list.sort(key=lambda r: r[1])
    return gene_list


def locate_gene_simple(snp_end_pos, gene_list):
    associated_gene_eids = []
    for gene in gene_list:
        start_pos = gene[1]
        stop_pos = gene[2]
        if snp_end_pos >= start_pos and snp_end_pos <= stop_pos:
            associated_gene_eids.append(gene[0])
    return associated_gene_eids


def cmp_list_str(list_1, list_2):
    list_1.sort()
    list_2.sort()
    if len(list_1) != len(list_2):
        return False
    for i in xrange(len(list_1)):
        if list_1[i] != list_2[i]:
            return False
    return True


def locate_genes(snp_end_pos, gene_list):
    """
    binary search gene
    Example
    -------
    gene_list = []
    gene_list.append(("gen2", 6, 10))
    gene_list.append(("gen1", 1, 5))
    gene_list.append(("gen4", 2, 3))
    gene_list.append(("gen3", 11, 15))
    for pos in xrange(20):
        res1 = locate_genes(pos, gene_list)
        res2 = locate_gene_simple(pos, gene_list)
        print "=================================="
        if not cmp_list_str(res1, res2):
            print "Error"
        print "pos=", pos
        print "Gen=", res1
    """
    associated_gene_eids = []
    # sort genes and remove not usefule genes
    start_pos_sorted_genes = gene_list
    start_pos_sorted_genes.sort(key=lambda r: r[1])
    sorted_start_positions = [r[1] for r in start_pos_sorted_genes]
    start_pos = bisect_right(sorted_start_positions, snp_end_pos) - 1
    if start_pos is not None:
        if start_pos >= 0 and start_pos < len(start_pos_sorted_genes) - 1:
            start_pos_sorted_genes = start_pos_sorted_genes[:start_pos + 1]
        if start_pos < 0:
            return associated_gene_eids
    start_pos_sorted_genes.sort(key=lambda r: r[2])
    stop_pos_sorted_genes = start_pos_sorted_genes
    sorted_stop_positions = [r[2] for r in stop_pos_sorted_genes]
    stop_pos = bisect_right(sorted_stop_positions, snp_end_pos) - 1
    if stop_pos is not None:
        if stop_pos < 0:
            stop_pos = 0
        stop_pos_sorted_genes = stop_pos_sorted_genes[stop_pos:]
    associated_gene_eids =\
        locate_gene_simple(snp_end_pos, stop_pos_sorted_genes)
    return associated_gene_eids


def import_chromosomes_db(store, path_chromosomes_json):
    chrs = import_chromosomes(path_chromosomes_json)
    for _chr in chrs:
        _chr = store.create_entity('Chromosome', **_chr)
    store.flush()


def import_genes_db(store,
                    path_chromosomes_json,
                    path_hg18_ref_gen_mate,
                    chr_map):
    genes = import_genes(path_chromosomes_json, path_hg18_ref_gen_mate)
    for gene in genes:
        #print 'gene', gene['name'], gene['chromosome']
        gene['chromosome'] = chr_map[gene['chromosome']]
        gene = store.create_entity('Gene', **gene)
    store.flush()


def import_study(data_dir):
    """Import a study from a data dir"""
    data = {}
    data['data_filepath'] = osp.abspath(data_dir)
    data['name'] = u'Localizer94'
    data['description'] = u'localizer db'
    return data


class NcbiSnpMapperConfig:
    def __init__(self,
                 snps_data_path,
                 line_num,
                 chr_map,
                 platform_eids,
                 platform_snps,
                 sorted_gene_list,
                 is_mute=False):
        self.snps_data_path = snps_data_path
        self.chr_map = chr_map
        self.platform_eids = platform_eids
        self.platform_snps = platform_snps
        self.sorted_gene_list = sorted_gene_list
        self.is_mute = is_mute
        self.line_num = line_num


def flush_lines_into_db(input_lines,
                        store,
                        is_mute,
                        chr_map,
                        platform_eids,
                        platform_snps,
                        sorted_gene_list,
                        store_flush_num=100000):
    isnp = 0
    for line in input_lines:
        words = line.split("\t")
        if len(words) > 0:
            isnp = isnp + 1
            snp = {}
            snp['rs_id'] = unicode(words[4])
            # Only the end position will be put here
            snp['position'] = int(words[3])
            snp['chromosome'] = chr_map[unicode(words[1])]
            # print "======================================"
            # print "words = ", words
            # print "snp = ", repr(snp)
            # Save into database
            snp_db = store.create_entity('Snp', **snp)
            add_rel_platform_snp(store=store,
                                 platform_eids=platform_eids,
                                 platform_snps=platform_snps,
                                 snp_rs_id=snp['rs_id'],
                                 snp_db=snp_db)
            # Look for all the gens and add relations
            gene_eids = locate_genes(snp['position'],
                                     sorted_gene_list)
            if gene_eids != []:
                for gene_eid in gene_eids:
                    store.relate(gene_eid,
                                 'snps_genes',
                                 snp_db.eid)
            if isnp % store_flush_num == 0:
                store.flush()
    store.flush()
    return isnp


def import_ncbi_snp_mapper(mapper_config):
    """import snps from ncbi dataset
    very time consuming process
    """
    ########################### Input parameters ############################
    snps_data_path = mapper_config.snps_data_path
    # store cannot be picklized so that we put it as global variable
    # store = mapper_config.store
    chr_map = mapper_config.chr_map
    platform_eids = mapper_config.platform_eids
    platform_snps = mapper_config.platform_snps
    sorted_gene_list = mapper_config.sorted_gene_list
    is_mute = mapper_config.is_mute
    line_num = mapper_config.line_num
    isnp = 0
    store_flush_num = 5000
    file_line_flush_num = store_flush_num
    input_lines = []
    len_input_lines = 0
    start_time = datetime.datetime.now()
    ########################### Import data ############################
    with open(snps_data_path) as infile:
        for line in infile:
            input_lines.append(line)
            len_input_lines = len_input_lines + 1
            isnp = isnp + 1
            if len_input_lines > file_line_flush_num:
                print "Start to flush input_lines"
                flush_lines_into_db(input_lines,
                                    store,
                                    is_mute,
                                    chr_map,
                                    platform_eids,
                                    platform_snps,
                                    sorted_gene_list,
                                    store_flush_num)
                input_lines = []
                len_input_lines = 0
                now_time = datetime.datetime.now()
                delta_time = now_time - start_time
                time_left_seconds = \
                    float(delta_time.seconds) / float(isnp) \
                    * (line_num - isnp)
                if not is_mute:
                    sys.stdout.write("%s minutes left" %
                                (repr(time_left_seconds / 60)) + "\n")
                    sys.stdout.write("Already import " +
                                repr(isnp) +
                                " snps into db." + "\n")
    flush_lines_into_db(input_lines,
                        store,
                        is_mute,
                        chr_map,
                        platform_eids,
                        platform_snps,
                        store_flush_num)
    return isnp


###############################################################################
### Genomics entities #########################################################
###############################################################################
# XXX These functions may be pushed in helpers, as they may be more general
def import_genomic_measures(measure_path, genetics_basename):
    """Import a genomic measures"""
    g_measures = {}
    # path to BED / BIM / FAM files
    bed_path = os.path.join(measure_path, genetics_basename + '.bed')
    bim_path = os.path.join(measure_path, genetics_basename + '.bim')
    fam_path = os.path.join(measure_path, genetics_basename + '.fam')
    # read FAM file as CSV file
    fam_file = open(fam_path, 'rU')
    fam_reader = csv.reader(fam_file, delimiter=' ')
    # one subject per line
    i = 0
    for row in fam_reader:
        print "row =", i
        i = i + 1
        subject_id = row[1]
        genomic_measure = {}
        genomic_measure['identifier'] = u'%s' % subject_id
        genomic_measure['type'] = u'SNP'
        genomic_measure['format'] = u'plink'
        genomic_measure['filepath'] = unicode(bed_path)
        genomic_measure['chip_serialnum'] = None
        genomic_measure['completed'] = True
        genomic_measure['valid'] = True
        genomic_measure['platform'] = None
        g_measures[subject_id] = genomic_measure
    return g_measures


###############################################################################
### MAIN ######################################################################
###############################################################################
if __name__ == '__main__':
    # Create store
    from cubicweb.dataimport import SQLGenObjectStore
    store = SQLGenObjectStore(session)
    sqlgen_store = True
    selected_opt = ""
    # root_dir = "/volatile/jinpeng/frouin/ncbi/scripts/ncbi"
    root_dir = osp.abspath(sys.argv[4])
    genetics_dir = osp.join(root_dir, 'genetics')
    if len(sys.argv) >= 6:
        selected_opt = sys.argv[5]
    if selected_opt == compute_opt.snps:
        sqlgen_store = False
        if len(sys.argv) >= 7:
            snps_data_path = sys.argv[6]
        else:
            snps_data_path = osp.join(genetics_dir, "snp138Common.txt")
    g_mes = 'qc_subjects_qc_genetics_all_snps_common.bim'  # 'Localizer94.bim'
    path_chromosomes_json = os.path.join(genetics_dir,
                                         'chromosomes.json')
    path_hg18_ref_gen_mate = os.path.join(genetics_dir,
                                          'hg18.refGene.meta')
    path_platforms = osp.join(root_dir, 'platforms')
    path_genome_wide_snp_6_na33_annot = osp.join(path_platforms,
                                                 "GenomeWideSNP_6.na33.annot.csv")
    path_human660w_quad_v1_h = osp.join(path_platforms, "human660w-quad_v1_h.bed")
    path_human610_quadv1_h = osp.join(path_platforms, "Human610-Quadv1_H.bed")
    ### Initialize genetics ####################################################
    # Import Chromosomes
    if sqlgen_store:
        import_chromosomes_db(store, path_chromosomes_json)
    chr_map = get_name_map_eid(session,
                               "Chromosome",
                               "name")
    # Import Genes
    if sqlgen_store:
        import_genes_db(store,
                        path_chromosomes_json,
                        path_hg18_ref_gen_mate,
                        chr_map)
    sorted_gene_list = get_sorted_genes_db(session)
    # Import three Platforms
    print "Processing platforms..."
    platforms = []
    platform = {'name': u'Affymetrix_6.0'}
    platforms.append(platform)
    platform = {'name': u'Illu_660'}
    platforms.append(platform)
    platform = {'name': u'Illu_610'}
    platforms.append(platform)
    if sqlgen_store:
        for platform in platforms:
            platform_db = store.create_entity('GenomicPlatform',
                                              **platform)
        store.flush()
    platform_eids = get_name_map_eid(session, "GenomicPlatform", "name")
    platform_snps = {}
    affymetrix_6_0_snps = read_snps_rsid_genome_wide_snp_6_na33_annot(
                                path_genome_wide_snp_6_na33_annot)
    platform_snps[u'Affymetrix_6.0'] = affymetrix_6_0_snps
    platform_snps[u'Illu_660'] = read_snps_human6xxw_quad_v1_h_bed(
                                    path_human660w_quad_v1_h)
    platform_snps[u'Illu_610'] = read_snps_human6xxw_quad_v1_h_bed(
                                    path_human610_quadv1_h)
    if selected_opt == compute_opt.snps:
        sys.stdout.write("Processing SNPs...\n")
        print "snps_data_path = ", snps_data_path
        line_num = line_numbers(snps_data_path)
        snp_mapper_config = NcbiSnpMapperConfig(
                                    snps_data_path=snps_data_path,
                                    line_num=line_num,
                                    chr_map=chr_map,
                                    platform_eids=platform_eids,
                                    platform_snps=platform_snps,
                                    sorted_gene_list=sorted_gene_list,
                                    is_mute=False)
        import_ncbi_snp_mapper(snp_mapper_config)


#    for snp_mapper_config in snp_mapper_configs:
#        import_ncbi_snp_mapper(snp_mapper_config)
#### Genetics measures #####################################################
#gen_measures = import_genomic_measures('genetics', g_mes.strip('.bim'))
#
## Flush/Commit
#if sqlgen_store:
#    store.flush()
#
#study = import_study(data_dir=root_dir)
#study = store.create_entity('Study', **study)
#
############################################################################
#### Subjects ##############################################################
############################################################################
#for sid in gen_measures.keys():
#    subject = {'identifier':sha1(gen_measures[sid]['identifier']).hexdigest(),
#               'gender':u'unknown',
#               'handedness':u'unknown',
#               'code_in_study':gen_measures[sid]['identifier']}
#    subject_eid = store.create_entity('Subject',**subject).eid
#    gen_assessment = {'identifier':sha1(gen_measures[sid]['identifier']+'ASS').hexdigest(),
#                      'age_for_assessment':0,
#                     }
#    gen_assessment_eid = store.create_entity('Assessment', **gen_assessment).eid
#    measure = gen_measures[sid]
#    measure['platform'] = platform.eid
#    measure['related_study'] = study.eid
#    keep_filepath = measure.pop('filepath')
#    measure_eid = store.create_entity('GenomicMeasure', **measure).eid
#    
#    fent_eid = store.create_entity('FileEntries',
#                                    name=unicode(keep_filepath),
#                                    filepath=unicode(keep_filepath)).eid
#    fset_eid = store.create_entity('FileSet',
#                                     name=unicode(keep_filepath),
#                                     fset_format=measure['format']).eid
#    store.relate(fset_eid, 'file_entries', fent_eid)                                 
#    store.relate(measure_eid, 'external_resources', fset_eid)
#    store.relate(measure_eid, 'concerns', subject_eid, subjtype='GenomicMeasure')
#    store.relate(gen_assessment_eid, 'generates', measure_eid, subjtype='Assessment')
## Flush/Commit
#if sqlgen_store:
#    store.flush()
#store.commit()
