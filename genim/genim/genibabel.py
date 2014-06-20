# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 16:16:52 2014

@author: vf140245
Copyrignt : CEA NeuroSpin - 2014
"""
import os
import numpy as np
import pandas as pd
from glob import glob
# import module to acces mart db and read plink file
from genomics_bioresrql import BioresourcesDB
import plinkio as ig


# Input data
#BASE_PATH = '/neurospin/brainomics/2013_imagen_bmi/'
#DATA_PATH = os.path.join(BASE_PATH, 'data')
#CLINIC_DATA_PATH = os.path.join(DATA_PATH, 'clinic')
#GENETICS_DATA_PATH = os.path.join(DATA_PATH, 'genetics')

# List from graff paper Nature 2012
bmi_gene_list = ['SEC16B', 'TNNI3K', 'PTBP2', 'NEGR1', 'LYPLAL1', 'LZTR2', 'LRP1B', 'TMEM18',
 'POMC', 'FANCL', 'CADM2', 'SLC39A8', 'FLJ3577', 'HMGCR', 'NCR3', 'AIF1',
 'BAT2', 'NUDT3', 'TFAP2B', 'MSRA', 'LRRN6C', 'LMX1B', 'BDNF', 'MTCH2',
 'RPL27A', 'TUB', 'FAIM2', 'MTIF3', 'NRXN3', 'PRKD1', 'MAP2K5', 'GPRC5B',
 'ADCY9', 'SH2B1', 'APOB48', 'FTO', 'MC4R', 'QPCTL', 'KCTD15', 'TMEM160',
 'PRL', 'PTER', 'MAF', 'NPC1']


def connect(verbose=True):
    """
    """
    BioresourcesDB.login('admin','alpine')
    s = BioresourcesDB.studies()
    if verbose:
        print "Studie(s) in DB (%d)"%(len(s))
        for i in s:
            print "      %s"%str(i)


def impute_data_by_med(data, verbose=0, nan_symbol=128):
   """ This function cut/pasted from B DaMota (genim-stat)
   """
   eps2 = 1e-17
   asNan = (data == nan_symbol)
   if verbose:
      print ('impute %d data for a total of %d' %
         (asNan[asNan].size, data.shape[0] * data.shape[1]))
   med = np.array([int(np.median(data[:, i]))
               for i in range(0, data.shape[1])])
   if med[med > 2].size > 0:
      print 'med == %s :'% str(nan_symbol), med[med > 2].size
      print 'med shape :', med.shape
      print 'shape of repetition', data.shape[0]
   else:
      med = np.array([np.median(data[:, i])
               for i in range(0, data.shape[1])])
      med[med == 0] = eps2
   med_all = np.repeat(med, data.shape[0]).reshape((-1, data.shape[0])).T
   data[asNan] = med_all[asNan]

   return data

def get_snps(gl, study):
    # Get GenomicMeasures eid linked to one study
    req = ('Any GM WHERE '
           'X is Assessment, X generates GM, GM is GenomicMeasure, '
           'X related_study RS, RS name "%(study)s"'%{'study':study}
           )
    gen_platform_list = [i[0]for i in BioresourcesDB.rql(req)]
    
    #get filepaths (should use results_file!!!! it does not work)
    genmeas_list = []
    for ol, peid in enumerate(gen_platform_list):
        req = ('Any FP WHERE '
               'X eid %(peid)d,  X filepath FP'%{'peid':peid})
        fp = [i[0]for i in BioresourcesDB.rql(req)][0]
        fp = fp.replace('/volatile/bioresource','/neurospin/brainomics/bioinformatics_resources')
        fn = glob(fp+'/*bim')[0]
        genmeas_list.append(fn)
        tmp = [i.split('\t')[1] for i in open(fn).read().split('\n')[:-1]]
        if (ol == 0):
            study_unviverse_snps = set(tmp)
        else:
            study_unviverse_snps = study_unviverse_snps.intersection(set(tmp))
    
    # These lines to be suppressed : add another gen measure in DB
    gfn = os.path.join('/neurospin/brainomics',
                   '2012_imagen_shfj',
                   'genetics',
                   'qc_sub_qc_gen_all_snps_common_autosome.bim')
    tmp = [i.split('\t')[1] for i in open(gfn).read().split('\n')[:-1]]
    study_unviverse_snps = study_unviverse_snps.intersection(set(tmp))
    # End these lines to be suppressed.
    
    # Now get snp info about genes
    snps = dict()
    for gene in gl:
        req = ('Any SN WHERE '
               'S is Snp, S rs_id SN, G is Gene, G name "%(g)s", '
               'S gene G'
                %{'g':gene})
        tmp = set([i[0] for i in BioresourcesDB.rql(req)]).intersection(study_unviverse_snps)
        snps[gene] = [str(i) for i in tmp]
    
    return snps, genmeas_list


def extract(genotype, snps_dict):
    """ from a genotype instance provide various helpers
    """
    void_gene = [i for i in snps_dict if len(snps_dict[i])==0]
    _ = [snps_dict.pop(i) for i in void_gene]
    col =  []
    _ = [col.extend(snps_dict[i]) for i in snps_dict]
    col = [str(i) for i in col]
    data = genotype.snpGenotypeByName(col)
    data = impute_data_by_med(data, verbose=True, nan_symbol=128)
    row = genotype.assayIID()

    return data, col, row, snps_dict, void_gene


def load_from_genes(geneList, study = None, snpDB='dbSNP139',geneDB='hg19', verbose=True):
    """ This function to read a snps pandas df from a gene list.
    Data are read from the locally dbSNP139 hg19 metainformation
    
    Parameters
    ----------
    geneList : string
        List of gene_names (eGene NCBI qualified names).

    study : string
        study name to be found in mart db.
    
    snpDB, geneDB : resp. string from [dbSNP139],[hg19]
        version of db
        
    verbose: boolean

    Returns
    -------
    snps_dict : dict
        keys are gens, values are snpList unicode
        returned value correspond to data available from the study
        
    void_gene : string
        list of gene with no snps in the study
        
    df : pandas dataframe
        index are IID and colnames are snps. Data are imputed (the raw way)
    """
    if snpDB != 'dbSNP139':
        raise RuntimeError("dbSNP139, hg19 only supported")
    if geneDB != 'hg19':
        raise RuntimeError("dbSNP139, hg19 only supported")
    
    # connect mart DB and get information on the gene
    connect(verbose=verbose)
    snps_dict, gfn_list = get_snps(geneList, study)
    if verbose:
        print ".....Genotype data read from: ",gfn_list
    
    # get the snp flesh data from the genotype file(s)
    gfn = os.path.join('/neurospin/brainomics',
                   '2012_imagen_shfj',
                   'genetics',
                   'qc_sub_qc_gen_all_snps_common_autosome')
    genotype = ig.Genotype(gfn)
    snp_data, snp_data_columns, snp_data_rows, snps_dict, void_gene = \
                                                  extract(genotype, snps_dict)
    df = pd.DataFrame(snp_data,index=snp_data_rows,
                              columns=snp_data_columns)
    return snps_dict, void_gene, df


if __name__ == "__main__":
    snps_dict, void_gene, df = load_from_genes(bmi_gene_list, study='IMAGEN')
    #examples                         
    a = df.loc[[u'000037509984', u'000044836688', u'000063400084'],:].values                         
    b = df.loc[[u'000037509984', u'000063400084', u'000044836688'],:].values
