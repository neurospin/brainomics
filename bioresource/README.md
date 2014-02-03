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

__Step1: Clean and Create Database for bioresource__

$ source brainomics/bioresource/scripts/clean_and_build_db.sh

This step is used to clean your cubicweb instance and database, and then build a new instance.

