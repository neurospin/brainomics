#!/usr/bin/python

from update.walk.dicomtarballs import walk_dicomtarballs

def main():
    # test over all Imagen FU2 DICOM files
    FU2_DICOMTARBALLS = '/neurospin/imagen/FU2/processed/dicomtarballs'
    walk_dicomtarballs(FU2_DICOMTARBALLS)


import logging
import sys

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())
