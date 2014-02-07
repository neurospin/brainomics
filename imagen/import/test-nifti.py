#!/usr/bin/python

from update.walk.nifti import walk_nifti

def main():
    # test all Imagen FU2 NIfTI files
    FU2_NIFTI = '/neurospin/imagen/FU2/processed/nifti'
    walk_nifti(FU2_NIFTI)


import sys
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())
