"""Index DAWBA data.

We receive DAWBA data as a set of files. We did not have FU2 files at the
time this was written. BL/FU1 files were typically submitted to directory
``/neurospin/imagen/RAW/PSC2/dawba``.

We have no control on the DAWBA data source. Instead we continuously monitor
``/neurospin/imagen/RAW/PSC2/dawba`` and check for updated files.

Whenever a DAWBA file changes, we discard all related DAWBA data from the
database and re-index the DAWBA file from scratch. The rationale is that the
initial Imagen team did the same when initially indexing BL/FU1 data in XNAT:
in their case, they used to discard all DAWBA data and re_indexing all DAWBA 
files.

"""
import logging
logger = logging.getLogger(__name__)

import os

from update.core.dawba import insert_dawba
from update.core.dawba import remove_dawba

from update.history import init_processing
from update.history import stop_processing


def monitor_dawba(root):
    """Index an incoming directory containing DAWBA files.

    Parameters
    ----------
    root : str
        Directory to explore.

    """
    for f in os.listdir(root):
        f_path = os.path.join(root, f)
        if os.path.isdir(f_path):
            logger.warn('Skip unexpected directory: %s'
                        % os.path.relpath(f_path, root))
        elif f.lower().endswith('.csv'):
            logger.debug('Process DAWBA file: %s'
                         % os.path.relpath(f_path, root))
            if init_processing(f_path):
                clean_dawba(f_path, root)
                index_dawba(f_path, root)
                stop_processing(f_path)
        else:
            logger.warn('Skip non-CSV file: %s'
                        % os.path.relpath(f_path, root))
