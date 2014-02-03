#Import all snps in paralle
#1: Use 'wc' to see how many lines in file $ wc /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt , for example 13749965
#2: Split the file into n parts, e.g. 7, which will run in paralle. Each file contains roughly 13749965/7 = 1964281 lines. Therefore run $ split -l 1964281 /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_
#3: Edit and run the below bash jobs in paralle.

CUBENAME=bioresource
INSTANCENAME=inst_$CUBENAME

cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_aa > ~/ncbi_logs/aa.log &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_ab > ~/ncbi_logs/ab.log &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_ac > ~/ncbi_logs/ac.log &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_ad > ~/ncbi_logs/ad.log &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_ae > ~/ncbi_logs/ae.log &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_af > ~/ncbi_logs/af.log &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_ag > ~/ncbi_logs/ag.log &

