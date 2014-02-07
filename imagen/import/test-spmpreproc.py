#!/usr/bin/python

from update.walk.spmpreproc import walk_spmpreproc

def main():
    # test all Imagen FU2 file preprocessed by SPM
    FU2_SPMPREPROC = '/neurospin/imagen/FU2/processed/spmpreproc'
    walk_spmpreproc(FU2_SPMPREPROC)


import sys
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())
