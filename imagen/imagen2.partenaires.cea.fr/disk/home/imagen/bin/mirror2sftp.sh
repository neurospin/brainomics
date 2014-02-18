#!/bin/sh

#
# When mirroring, use the following rsync options:
# -r  recurse into directories
# -l  copy symlinks as symlinks
# -t  preserve modification times
#
# Avoid -a because it would pull other options we want to avoid.
#

# QC - needs no anonymization
rsync -rlt /neurospin/imagen/RAW/PSC2/QC /chroot/data/BL/RAW/PSC2/
rsync -rlt /neurospin/imagen/FU2/RAW/PSC2/QC /chroot/data/FU2/RAW/PSC2/

# sftp_mirror
rsync -rlt /neurospin/imagen/FU2/processed/sftp_mirror/ /chroot/data/FU2/processed

# clean up
chmod -R g-w,o-w /chroot/data
