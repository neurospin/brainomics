#!/bin/sh

ROOT_TARGET='/chroot/data'


#
# When mirroring, use the following rsync options:
# -r  recurse into directories
# -l  copy symlinks as symlinks
# -t  preserve modification times
#
# Avoid -a because it would pull other unwanted options:
# -p  preserve permissions
# -g  preserve group
# -o  preserve owner
# -D  same as --devices --specials
# 


# FU2 - QC
# needs no anonymization
rsync -rlt \
    /neurospin/imagen/FU2/RAW/PSC2/QC \
    ${ROOT_TARGET}/FU2/RAW/PSC2/


# Psytools - FU2 data only!
# still anonymized by Scito
rsync -rlt \
    /neurospin/imagen/RAW/PSC2/psytools/*FU2*.csv \
    ${ROOT_TARGET}/FU2/RAW/PSC2/psytools/


# FU2 - processed
rsync -rlt \
    /neurospin/imagen/FU2/processed/nifti \
    /neurospin/imagen/FU2/processed/spmpreproc \
    /neurospin/imagen/FU2/processed/spmstatsintra \
    ${ROOT_TARGET}/FU2/processed/


# FU2 - processed_ftp
rsync -rlt \
    /neurospin/imagen/FU2/processed_ftp/nifti \
    /neurospin/imagen/FU2/processed_ftp/spmpreproc \
    /neurospin/imagen/FU2/processed_ftp/spmstatsintra \
    ${ROOT_TARGET}/FU2/processed/


# clean up
chmod -R g-w,o-w ${ROOT_TARGET}
find ${ROOT_TARGET} -type f -exec chmod -x {} \;
