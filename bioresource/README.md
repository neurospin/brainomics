bioresource
===========

Dependencies
------------

You need to use hg install those cubes on your computer:

```
hg clone http://hg.logilab.org/review/cubes/brainomics
hg clone http://hg.logilab.org/review/cubes/genomics
hg clone http://hg.logilab.org/review/cubes/questionnaire
hg clone http://hg.logilab.org/review/cubes/bootstrap
hg clone http://hg.logilab.org/review/cubes/squareui
hg clone http://hg.logilab.org/review/cubes/neuroimaging
hg clone http://hg.logilab.org/review/cubes/medicalexp
```

Since the newest version is not stable, you need older version instead.

I have tested my scripts on those versions:

```
* bootstrap     cubicweb-bootstrap-centos-version-0.4.0-1:cubicweb-bootstrap-debian-version-0.4.0-1:cubicweb-bootstrap-version-0.4.0
* brainomics    cubicweb-brainomics-debian-version-0.7.0
* card          0.5.3
* comment       1.9.1
* file          1.15.0
* forgotpwd     0.4.2
* genomics      cubicweb-genomics-debian-version-0.6.0
* jqplot        0.4.0
* medicalexp    cubicweb-medicalexp-debian-version-0.7.0
* neuroimaging  cubicweb-neuroimaging-debian-version-0.5.0
* preview       1.0.0
* questionnaire cubicweb-questionnaire-debian-version-0.5.0
* registration  0.4.2
* seo           0.2.0
* squareui      r 16
* trustedauth   0.3.0
```

How to import data
------------------

__Step 1: Clean and Create Database for bioresource__

```
$ source brainomics/bioresource/scripts/clean_and_build_db.sh
```

This step is used to clean your cubicweb instance and database, and then build a new instance.

__Step 2 : Import chromosome, gene, platform information into database.__

```
$ source brainomics/bioresource/scripts/import_ncbi_part1.sh
```

__Step 3 : Clean ncbi snps file__

In the file "/neurospin/brainomics/2014_bioresource/data/snps/snp138Common.txt",
thre are some duplicated snps (the same rsxxxxx) and snps with unkown chromosomes,
this script is used to clean up snps. 

```
$ python brainomics/bioresource/scripts/clean_ncbi_duplicated_snp_data.py
```

This script will produce "/neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt"

__Step 4 : Import snps in paralle__

1: Use 'wc' to see how many lines in file 

```
$ wc /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt
```

For example there are 13749965 lines.


2: Split the file into n parts, e.g. 7, which will run in paralle. Each file contains roughly 13749965/7 = 1964281 lines. Therefore run 


```
$ split -l 1964281 /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt /neurospin/brainomics/2014_bioresource/data/snps/cleaned_snp138Common.txt_part_
```


3: Edit and run the below bash jobs in paralle.


```
$ source brainomics/bioresource/scripts/import_ncbi_part2.sh
```
