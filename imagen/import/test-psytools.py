#!/usr/bin/python

from update.monitor.psytools import monitor_psytools

def main():
    # test all Imagen FU2 Psytools files
    PSYTOOLS = '/neurospin/imagen/RAW/PSC2/psytools'
    PATTERN_FU2 = 'FU2'
    monitor_psytools(PSYTOOLS, PATTERN_FU2)


import sys
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())
