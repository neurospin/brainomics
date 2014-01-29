#!/usr/bin/python

from update.monitor.raw import monitor_raw

def main():
    # test all Imagen FU2 "raw packages"
    RAW_FU2 = '/neurospin/imagen/FU2/RAW/PSC2'
    monitor_raw(RAW_FU2)


import sys
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())
