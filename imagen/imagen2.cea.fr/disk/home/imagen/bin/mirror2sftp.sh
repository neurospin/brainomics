#!/bin/sh

# QC - needs no anonymization
rsync -r /neurospin/imagen/RAW/PSC2/QC /chroot/data/BL/RAW/PSC2/
rsync -r /neurospin/imagen/FU2/RAW/PSC2/QC /chroot/data/FU2/RAW/PSC2/

# sftp_mirror
rsync -r /neurospin/imagen/FU2/processed/sftp_mirror/ /chroot/data/FU2/processed

# clean up
chown -Rh imagen:imagen /chroot/data
chmod -R g-w,o-w /chroot/data
