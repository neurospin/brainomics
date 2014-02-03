#Import all snps in paralle
#1: Use 'wc' to see how many lines in file $ wc /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt , for example 14056008
#2: Split the file into n parts, e.g. 7, which will run in paralle. Each file contains roughly 14056008/7 = 2008002 lines. Therefore run $ split -l 2008002 /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_
#3: Edit and run the below bash jobs in paralle.

CUBENAME=bioresource
INSTANCENAME=inst_$CUBENAME

cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_aa > ~/ncbi_logs/ &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_ab > ~/ncbi_logs/ &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_ac > ~/ncbi_logs/ &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_ad > ~/ncbi_logs/ &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_ae > ~/ncbi_logs/ &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_af > ~/ncbi_logs/ &
cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data SNPS /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_ag > ~/ncbi_logs/ &

