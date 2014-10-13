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
##### FILES ARE NOT COMPLETELY ANONYMIZED (id_check_dob)
#rsync -rlt \
#    /neurospin/imagen/RAW/PSC2/psytools/*FU2*.csv \
#    ${ROOT_TARGET}/FU2/RAW/PSC2/psytools/

# Psytools - except FU2!
# had been anonymized by Scito
##### FILES ARE NOT COMPLETELY ANONYMIZED (id_check_dob)
#rsync -rlt \
#    --exclude '*FU2*.csv' \
#    /neurospin/imagen/RAW/PSC2/psytools/*.csv \
#    ${ROOT_TARGET}/BL_FU1/RAW/PSC2/psytools/

# DAWBA - BL/FU1
# recent exports not in XNAT, anonymized by us
rsync -rlt \
    /neurospin/imagen/RAW/PSC2/dawba/*.txt \
    ${ROOT_TARGET}/BL_FU1/RAW/PSC2/dawba/

# DAWBA - FU2
# anonymized by us
rsync -rlt \
    /neurospin/imagen/FU2/RAW/PSC2/dawba/*.txt \
    ${ROOT_TARGET}/FU2/RAW/PSC2/dawba/

# fMRI preprocessing
mkdir -p ${ROOT_TARGET}/BL_FU1/processed/spmpreproc
( cd /neurospin/imagen/processed/spmpreproc ; tar cf - \
    */*/EPI_faces/job_preproc_*.m \
    */*/EPI_stop_signal/job_preproc_*.m \
) | ( cd ${ROOT_TARGET}/BL_FU1/processed/spmpreproc ; tar xf - )

# fMRI processing
mkdir -p ${ROOT_TARGET}/BL_FU1/processed/spmstatsintra
( cd /neurospin/imagen/processed/spmstatsintra ; tar cf - \
    */*/EPI_faces/swea/job_spmstatsintra_*.m \
    */*/EPI_faces/swea/rpL_*.txt \
    */*/EPI_faces/swea/SPM.mat.gz \
    */*/EPI_stop_signal/swea/job_spmstatsintra_*.m \
    */*/EPI_stop_signal/swea/rpL_*.txt \
    */*/EPI_stop_signal/swea/SPM.mat.gz \
) | ( cd ${ROOT_TARGET}/BL_FU1/processed/spmstatsintra ; tar xf - )

# FU2 - aMRI
# needs no anonymization
rsync -rlt \
    /neurospin/imagen/FU2/processed/nifti \
    ${ROOT_TARGET}/FU2/processed/

# genetics
mkdir -p ${ROOT_TARGET}/BL_FU1/genetic/qc/imput/610/Mach_HapMap
rsync -rlt \
    /neurospin/imagen/genetic/qc/imput/610/Mach_HapMap/chroms \
    /neurospin/imagen/genetic/qc/imput/610/Mach_HapMap/plink \
    ${ROOT_TARGET}/BL_FU1/genetic/qc/imput/610/Mach_HapMap/
mkdir -p ${ROOT_TARGET}/BL_FU1/genetic/qc/imput/610/Mach_1kG
rsync -rlt \
    /neurospin/imagen/genetic/qc/imput/610/Mach_1kG/chroms \
    ${ROOT_TARGET}/BL_FU1/genetic/qc/imput/610/Mach_1kG/
mkdir -p ${ROOT_TARGET}/BL_FU1/genetic/qc/imput/660/Mach_HapMap
rsync -rlt \
    /neurospin/imagen/genetic/qc/imput/660/Mach_HapMap/chroms \
    /neurospin/imagen/genetic/qc/imput/660/Mach_HapMap/plink \
    ${ROOT_TARGET}/BL_FU1/genetic/qc/imput/660/Mach_HapMap/
mkdir -p ${ROOT_TARGET}/BL_FU1/genetic/qc/imput/union/Mach_1kG
rsync -rlt \
    /neurospin/imagen/genetic/qc/imput/union/Mach_1kG/chroms \
    ${ROOT_TARGET}/BL_FU1/genetic/qc/imput/union/Mach_1kG/
mkdir -p ${ROOT_TARGET}/BL_FU1/genetic/qc/imput/union/Mach_HapMap
rsync -rlt \
    /neurospin/imagen/genetic/qc/imput/union/Mach_HapMap/plink \
    ${ROOT_TARGET}/BL_FU1/genetic/qc/imput/union/Mach_HapMap/


# clean up
chmod -R g-w,o-w ${ROOT_TARGET}
find ${ROOT_TARGET} -type f -exec chmod -x {} \;
