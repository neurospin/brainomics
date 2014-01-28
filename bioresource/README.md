bioresource
===========

Dependencies
------------

You need to first install those cubes on your computer:

```
hg clone http://hg.logilab.org/review/cubes/brainomics
hg clone http://hg.logilab.org/review/cubes/genomics
hg clone http://hg.logilab.org/review/cubes/questionnaire
hg clone http://hg.logilab.org/review/cubes/medicalexp
hg clone http://hg.logilab.org/review/cubes/neuroimaging

hg clone http://hg.logilab.org/review/cubes/bootstrap
hg clone http://hg.logilab.org/review/cubes/squareui
```

The above cubes have depencies that can be installed as system packages.
On Ubuntu:

```
cubicweb-card
cubicweb-comment
cubicweb-dataio
cubicweb-file
cubicweb-dataio
cubicweb-jqplot
```

Since the newest version may be broken, you need stable version instead, for example:

```
hg clone -u stable http://hg.logilab.org/review/cubes/registration
```

squareui needs to roll back into this version
```
$ hg clone http://hg.logilab.org/review/cubes/squareui
$ hg up -r 292de533fa69

changeset:   26:292de533fa69
user:        Katia Saurfelt <katia.saurfelt@logilab.fr>
date:        Fri Oct 18 15:33:37 2013 +0200
summary:     [facets] add missing DATA_URL javascript variable definition (closes #3230380)
```
