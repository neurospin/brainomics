import sys
from numpy import unique

sys.path.append('/home/vf140245/gits/bioresources/python')
import bioresourcesdb
from bioresourcesdb import BioresourcesDB
sys.path.append('/home/vf140245/gits/igutils')
import igutils as ig


BioresourcesDB.login('admin','admin')
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
gene_list = ['SERPINB1', 'KIF1B', 'PER3']
snps = dict()
for gene in gene_list:
    req = ('Any G,B,E,SN '
           'WHERE G name "%(g)s", G start_position B, '
                 'G stop_position E, S is Snp,  S rs_id SN, '
                 'S position SP HAVING SP > B, SP < E'
          %{'g':gene})
    snps[gene] = BioresourcesDB.rql(req)

# confront this list to the availabe data
req = ('Any GM, GP, I '
        'WHERE GM is GenomicMeasure, GM platform GP, GP name I')
req_ret = BioresourcesDB.rql(req)
gpl_eid = unique([i[1] for i in req_ret if i[2].startswith('Ill')]).tolist()
platform = dict()
for eid in gpl_eid:
    req=('Any N ' 
         'WHERE GP is GenomicPlatform, '
                'GP eid %(eid)d , GP name N'
        %{'eid':eid})
    name = BioresourcesDB.rql(req)[0][0]
    req=('Any SN ' 
         'WHERE GP is GenomicPlatform, '
                'GP eid %(eid)d , GP related_snps S, S rs_id SN'
        %{'eid':eid})
    req_ret = [i[0] for i in BioresourcesDB.rql(req)]
    platform[name] = req_ret
print "Platform stats"
for i in platform:
    print "  %s Num SNPs %d"%(i,len(platform[i]))
s = set(platform[platform.keys()[0]])
for i in platform.keys()[1:]:
    s = s.intersection(set(platform[i]))
print "intersect %d"%len(s)


