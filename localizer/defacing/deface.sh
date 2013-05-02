#!/bin/bash

SOURCE_DIR='/neurospin/brainomics/2012_brainomics_localizer/data/subjects'
OUTPUT_DIR='/volatile/2012_brainomics_localizer/data/subjects'

# configure FreeSurfer
FREESURFER_HOME='/i2bm/local/freesurfer'
export FREESURFER_HOME
. ${FREESURFER_HOME}/FreeSurferEnv.sh

# iterate over source 'anat.nii.gz' T1 files
for subject in "${SOURCE_DIR}/"*
do
    subject=`basename "$subject"`
    # create output directory
    mkdir -p "${OUTPUT_DIR}/${subject}/anat"
    # output directory will contain 'anat_defaced.nii.gz' and log file
    cd "${OUTPUT_DIR}/${subject}/anat"
    mri_deface \
        "${SOURCE_DIR}/${subject}/anat/anat.nii.gz" \
        "${FREESURFER_HOME}/average/talairach_mixed_with_skull.gca" \
        "${FREESURFER_HOME}/average/face.gca" \
        'anat_defaced.nii.gz'
done
