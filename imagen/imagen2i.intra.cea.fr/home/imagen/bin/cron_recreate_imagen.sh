#!/bin/sh

# stop all CubicWeb instances
service cubicweb stop

# delete and create the Imagen instance anew
# create entities such as CWUser in postcreate.py
### cubicweb-ctl ???

# start all CubiCWeb instances
service cubicweb start
