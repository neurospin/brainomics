#!/bin/sh

# temporary file to dump CWUsers to
FILE='/root/tmp.cwusers.txt'

# dump CWUsers
cubicweb-ctl shell imagen /home/imagen/bin/dump_cwusers.py > "$FILE"

# stop all CubicWeb instances
service cubicweb stop

# delete and create the Imagen instance anew
# create entities such as CWUser in postcreate.py
### cubicweb-ctl ???

# delete temporary file with CWUsers
rm -f "$FILE"

# start all CubiCWeb instances
service cubicweb start
