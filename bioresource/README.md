bioresource
===========

Dependencies
------------

You need to first install those cubes on your computer:

```
hg clone http://hg.logilab.org/review/cubes/genomics
hg clone http://hg.logilab.org/review/cubes/brainomics
hg clone http://hg.logilab.org/review/cubes/questionnaire


hg clone http://hg.logilab.org/review/cubes/bootstrap
hg clone http://hg.logilab.org/review/cubes/card
hg clone http://hg.logilab.org/review/cubes/comment
hg clone http://hg.logilab.org/review/cubes/dataio

hg clone http://hg.logilab.org/review/cubes/file
hg clone http://hg.logilab.org/review/cubes/dataio
hg clone http://hg.logilab.org/review/cubes/forgotpwd
hg clone http://hg.logilab.org/review/cubes/jqplot

hg clone http://hg.logilab.org/review/cubes/medicalexp
hg clone http://hg.logilab.org/review/cubes/neuroimaging
hg clone http://hg.logilab.org/review/cubes/registration
hg clone http://hg.logilab.org/review/cubes/squareui

hg clone http://hg.logilab.org/review/cubes/trustedauth
hg clone http://hg.logilab.org/review/cubes/vtimeline
```

Since the newest version may be broken, you need stable version instead, for example:

```
hg clone -u stable http://hg.logilab.org/review/cubes/registration
```

squareui needs to roll back into this version
```
hg clone http://hg.logilab.org/review/cubes/squareui

changeset:   16:e7863ce5b727
user:        Katia Saurfelt <katia.saurfelt@logilab.fr>
date:        Fri Oct 18 15:33:37 2013 +0200
summary:     [facets] add missing DATA_URL javascript variable definition (closes #3230380)
```



