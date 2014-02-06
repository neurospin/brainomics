# This script will be terminated very fast
CUBENAME=bioresource
INSTANCENAME=inst_$CUBENAME

cubicweb-ctl shell $INSTANCENAME ./import_ncbi.py /neurospin/brainomics/2014_bioresource/data
