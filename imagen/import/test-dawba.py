#!/usr/bin/python

from update.monitor.dawba import monitor_dawba

def main():
    # test all Imagen BL/FU1 DAWBA files
    DAWBA = '/neurospin/imagen/RAW/PSC2/dawba'
    monitor_dawba(DAWBA)


import sys
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())
