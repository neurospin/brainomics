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
    /neurospin/imagen/FU2/RAW/PSC2_FIXED/QC \
    ${ROOT_TARGET}/FU2/RAW/PSC2/

# Psytools - FU2 only!
# still anonymized by Scito
rsync -rlt \
    /neurospin/imagen/RAW/PSC2/psytools/*FU2*.csv \
    ${ROOT_TARGET}/FU2/RAW/PSC2/psytools/

# Psytools - except FU2!
# had been anonymized by Scito
rsync -rlt \
    --exclude '*FU2*.csv' \
    /neurospin/imagen/RAW/PSC2/psytools/*.csv \
    ${ROOT_TARGET}/BL_FU1/RAW/PSC2/psytools/

# DAWBA
# had been anonymized by Scito
rsync -rlt \
    /neurospin/imagen/RAW/PSC2/dawba/*.csv \
    ${ROOT_TARGET}/BL_FU1/RAW/PSC2/dawba/

# statistics for faces task + swea preprocessing
mkdir -p ${ROOT_TARGET}/BL_FU1/processed/spmstatsintra
( cd /neurospin/imagen/processed/spmstatsintra ; tar cf - \
    */*/EPI_faces/swea/job_spmstatsintra_*.m \
    */*/EPI_faces/swea/SPM.mat.gz \
) | ( cd ${ROOT_TARGET}/BL_FU1/processed/spmstatsintra ; tar xf - )


# FU2 - aMRI
# needs no anonymization
rsync -rlt \
    /neurospin/imagen/FU2/processed/nifti \
    ${ROOT_TARGET}/FU2/processed/

# clean up
chmod -R g-w,o-w ${ROOT_TARGET}
find ${ROOT_TARGET} -type f -exec chmod -x {} \;
