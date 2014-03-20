#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from numpy import unique, vstack
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir, 'python'))
from bioresourcesdb import BioresourcesDB

#https://github.com/VincentFrouin/igutils.git
sys.path.append('/home/vf140245/gits/igutils')
import igutils as ig


BioresourcesDB.login('admin', 'admin')
BioresourcesDB.studies()

#a = BioresourcesDB.rql('Any S,N  WHERE S is Study, S name N')
#gene='KIF1B'
#req = 'Any G,B,E,SN WHERE G name "%(g)s", G start_position B, G stop_position E, S is Snp,  S rs_id SN ,S position SP HAVING SP > B, SP < E'%{'g':gene}
#a = BioresourcesDB.rql(req)          
 
 
#gene_list = [
#'CFB','S1PR4','DLGAP2','FBXL14','CDK7','LY6G6C','LY6G6E','LPCAT1',
#'C16orf59','SYT8','LOC728613','SFTA2','FKBP1A','LOC100508120',
#'UBOX5-AS1','HAGH','PCSK4','HN1L','GUSBP3','CSNK1G2','SERPINB1'] 

# get the snps availables reference 1000G hg19 dbSNP139
# this is the reference snps available

start_time = datetime.now()

def snps_in_gene(database, gene):
    """Return all SNPs associated to a gene.

    Parameters
    ----------
    database : ?
        Bioresource database.

    gene : unicode
        Gene name.

    Returns
    -------
    array_like
        List of rsIDs in gene.

    """
    req = ("Any RS WHERE G name '%(gene)s', "
           "G start_position B, G stop_position E, "
           "S is Snp, S rs_id RS, S position SP HAVING SP > B, SP < E"
           % {'gene': gene})
    return [i[0] for i in database.rql(req)]


genes = ('SERPINB1', 'KIF1B', 'PER3', 'UBR4')
snps = {}
for gene in genes:
    snps[gene] = snps_in_gene(BioresourcesDB, gene)


def genomic_measures(database):
    """Return all genomic measures in database.

    Parameters
    ----------
    database : ?
        Bioresource database.

    Returns
    -------
    dict
        Dictionary of genomic measures with measure eid as keys
        and plaform name as values.

    """
    req = ("Any GM, N WHERE GM is GenomicMeasure, "
           "GM platform GP, GP name N")
    return {m[0]: m[1] for m in database.rql(req)}


def snps_in_platform(database, platform):
    """Return all SNPs measured by a platform.

    Parameters
    ----------
    database : ?
        Bioresource database.

    platform : unicode
        Platform name.

    Returns
    -------
    array_like
        List of rsIDs measured by platform.

    """
    req = ("Any RS WHERE GP is GenomicPlatform, "
           "GP name '%(name)s', GP related_snps S, S rs_id RS"
           % {'name': platform})
    return [i[0] for i in database.rql(req)]


# SNPs for platforms associated GenomicMeasure
measures = genomic_measures(BioresourcesDB)
platform = {}
for p in set(measures.values()):
    if p.startswith('Illu'):
        platform[p] = snps_in_platform(BioresourcesDB, p)

print 'Platform stats'
intersection = None
for name, snps in platform.iteritems():
    print '  %s: %d SNPs' % (name, len(snps))
    if intersection:
        intersection &= set(snps)
    else:
        intersection = set(snps)
print '  intersection: %d SNPs' % len(intersection)


# consider the subjects
#
genemeasureSubj = {}
genemeasureFP = {}
for eid in measures.keys():
    req =('Any SN WHERE S is Subject, S identifier SN, '
          'S concerned_by AS, AS generates GM, GM eid %(eid)d'
         %{'eid':eid})
    genemeasureSubj[eid] = [i[0]  for i in BioresourcesDB.rql(req)]
    req =('Any FP WHERE GM  eid %(eid)d, GM filepath FP'
         %{'eid':eid})    
    genemeasureFP[eid] = BioresourcesDB.rql(req)[0][0]

base_subject = {}
for eid in measures.keys():
    base_subject[eid] = genemeasureSubj[eid]

# focus on gene UBR4
# snps present sur la puce (doit lever les snp qui auraient disparus!!)
#
snps_in_ubr4 = snps_in_gene(BioresourcesDB, 'UBR4')
ubr4 = {}
for name, snps in platform.iteritems():
    ubr4[name] = set(snps_in_ubr4) & set(platform[name])
    print 'gene UBR4 sur puce %s: %d SNPs' % (name, len(ubr4[name]))

print 'Request on a few genes: ', datetime.now() - start_time

start_time = datetime.now() 

snp_data=dict()
genotypeCommonSnp = dict()
for eid in gm_dir:
    genotype = ig.Geno(genemeasureFP[eid])
    genotypeSnp = genotype.snpList().tolist()
    genotypeCommonSnp[eid] = list(set(genotypeSnp).intersection(set([str(i) for i in urb[gm_dir[eid]]])))
    genotype.setOrderedSubsetIndiv([str(i) for i in genemeasureSubj[eid]])
    snp_data[eid] = genotype.snpGenotypeByName(genotypeCommonSnp[eid])    
    print 'Reading/Parsing genofile: ', datetime.now() - start_time
    start_time = datetime.now()

print base_subject.keys()
print gm_dir.keys()
print snp_data.keys()
print genemeasureFP.keys()
print genemeasureSubj.keys()
print genotypeCommonSnp.keys()


#encore une derniere intersection entre ce qui est vu sur ente toutes les plateforme
# et encore un dernier re-ordering des snp
grandCommonSnp = set(genotypeCommonSnp[gm_dir.keys()[0]])
grandCommonSnpIndex = dict()
for eid in gm_dir.keys()[1:]:
    grandCommonSnp = grandCommonSnp.intersection(set(genotypeCommonSnp[eid]))
for eid in gm_dir:
    grandCommonSnpIndex[eid] = [genotypeCommonSnp[eid].index(i) for i in grandCommonSnp]

for eid in gm_dir:
    snp_data[eid] = snp_data[eid][:,grandCommonSnpIndex[eid]]

# je sais pas faire en boucle
tmp = tuple(gm_dir.keys())
grand_snp_data = vstack((snp_data[tmp[0]], snp_data[tmp[1]], snp_data[tmp[2]]))
grand_subject  = genemeasureSubj[tmp[0]] + genemeasureSubj[tmp[1]]  + genemeasureSubj[tmp[2]] 
gran_chip = []
for eid in gm_dir:
    gran_chip += [gm_dir[eid]]*len(genemeasureSubj[eid])


print 'Reordering/subseting data: ', datetime.now() - start_time
 
print 'Grand SNP data (grand_snp_data):', grand_snp_data.shape
print 'Grand Subject Ordered List(grand_subject):', len(grand_subject)
print 'Data collated from GenomicMeasures:'
for eid in gm_dir:
    print '     [%s]\n     hybridized on chip %s'%(genemeasureFP[eid], gm_dir[eid])

