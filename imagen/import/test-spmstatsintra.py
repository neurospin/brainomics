#!/usr/bin/python

from update.walk.spmstatsintra import walk_spmstatsintra

def main():
    # test all Imagen FU2 files processed by SPM
    FU2_SPMSTATSINTRA = '/neurospin/imagen/FU2/processed/spmstatsintra'
    walk_spmstatsintra(FU2_SPMSTATSINTRA)


import sys
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())
