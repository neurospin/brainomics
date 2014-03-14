#Import all snps in parallel
#1: Use 'wc' to see how many lines in file $ wc /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt , for example 13749965
#2: Split the file into n parts, e.g. 7, which will run in parallel. Each file contains roughly 13749965/7 = 1964281 lines. Therefore run $ split -l 1964281 /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_
#3: Edit and run the below bash jobs in paralle.

CUBENAME=bioresource
INSTANCENAME=inst_$CUBENAME
LOGDIRPATH=~/ncbi_logs
BIORES_DATA_ROOT=/neurospin/brainomics/2014_bioresource/data

(unbuffer cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py $BIORES_DATA_ROOT SNPS $BIORES_DATA_ROOT/snps/cleaned_snp138Common.txt_part_aa > $LOGDIRPATH/aa.log &)  
(unbuffer cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py $BIORES_DATA_ROOT SNPS $BIORES_DATA_ROOT/snps/cleaned_snp138Common.txt_part_ab > $LOGDIRPATH/ab.log &)
(unbuffer cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py $BIORES_DATA_ROOT SNPS $BIORES_DATA_ROOT/snps/cleaned_snp138Common.txt_part_ac > $LOGDIRPATH/ac.log &)
(unbuffer cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py $BIORES_DATA_ROOT SNPS $BIORES_DATA_ROOT/snps/cleaned_snp138Common.txt_part_ad > $LOGDIRPATH/ad.log &)
(unbuffer cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py $BIORES_DATA_ROOT SNPS $BIORES_DATA_ROOT/snps/cleaned_snp138Common.txt_part_ae > $LOGDIRPATH/ae.log &)
(unbuffer cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py $BIORES_DATA_ROOT SNPS $BIORES_DATA_ROOT/snps/cleaned_snp138Common.txt_part_af > $LOGDIRPATH/af.log &)
(unbuffer cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py $BIORES_DATA_ROOT SNPS $BIORES_DATA_ROOT/snps/cleaned_snp138Common.txt_part_ag > $LOGDIRPATH/ag.log &)

