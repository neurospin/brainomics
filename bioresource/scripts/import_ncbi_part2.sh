#Import all snps in paralle
#1: Use 'wc' to see how many lines in file $ wc /neurospin/brainomics/2014_bioresource/data/snps/snp138Common.txt, for example 14056510 
#2: Split the file into n parts, e.g. 7, which will run in paralle. Each file contains roughly 14056510/7 = 2008073 lines. Therefore run $ split -l 2008073 /neurospin/brainomics/2014_bioresource/data/snps/snp138Common.txt snp138Common.txt_part_
#3: Edit and run the below bash jobs in paralle.

CUBENAME=bioresource
INSTANCENAME=inst_$CUBENAME

cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/snp138Common.txt_part_aa &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/snp138Common.txt_part_ab &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/snp138Common.txt_part_ac &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/snp138Common.txt_part_ad &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/snp138Common.txt_part_ae &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/snp138Common.txt_part_af &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/snp138Common.txt_part_ag &

