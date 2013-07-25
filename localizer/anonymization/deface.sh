#!/bin/bash

SOURCE_DIR='/neurospin/brainomics/2012_brainomics_localizer/data'
OUTPUT_DIR='/volatile/2012_brainomics_localizer/data'

# configure FreeSurfer
FREESURFER_HOME='/i2bm/local/freesurfer'
export FREESURFER_HOME
. ${FREESURFER_HOME}/FreeSurferEnv.sh

# process subjects
for subject in "${SOURCE_DIR}/subjects/"*
do
    subject=`basename "$subject"`
    # create output directory
    mkdir -p "${OUTPUT_DIR}/subjects/${subject}/anat"
    # log file will be written into current directory
    cd "${OUTPUT_DIR}/subjects/${subject}/anat"
    # anat.nii.gz -> anat_defaced.nii.gz
    mri_deface \
        "${SOURCE_DIR}/subjects/${subject}/anat/anat.nii.gz" \
        "${FREESURFER_HOME}/average/talairach_mixed_with_skull.gca" \
        "${FREESURFER_HOME}/average/face.gca" \
        'anat_defaced.nii.gz'
    # raw_anat.nii.gz -> raw_anat_defaced.nii.gz
    mri_deface \
        "${SOURCE_DIR}/subjects/${subject}/anat/raw_anat.nii.gz" \
        "${FREESURFER_HOME}/average/talairach_mixed_with_skull.gca" \
        "${FREESURFER_HOME}/average/face.gca" \
        'raw_anat_defaced.nii.gz'
done
