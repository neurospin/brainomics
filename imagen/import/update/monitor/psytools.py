"""Index Psytools data.

Psytools FU2 data are submitted to ``/neurospin/imagen/RAW/PSC2/psytools``
alongside BL/FU1 data. Files specific to FU2 are identified by the ``FU2``
string in their name.

We have no control on the Pystools data source. Instead we continuously monitor
``/neurospin/imagen/RAW/PSC2/psytools`` and check for updated files.

Whenever a Pystools file changes, we discard all related Pystools data from the
database and re-index the Pystools file from scratch. This is not necessarily
the procedure followed by the initial Imagen team, altough the result ought to
be the same: we will have to look into it more closely!

"""
import logging
logger = logging.getLogger(__name__)

import os

from update.core.psytools import insert_psytools
from update.core.psytools import remove_psytools

from update.history import init_processing
from update.history import stop_processing


def monitor_psytools(root, pattern=None):
    """Index a directory containing Psytools files.

    Parameters
    ----------
    root : str
        Directory to explore.
    pattern : str
        Take into account only filenames matching ``pattern``.

    """
    for f in os.listdir(root):
        f_path = os.path.join(root, f)
        if os.path.isdir(f_path):
            logger.warn('Skip unexpected directory: %s'
                        % os.path.relpath(f_path, root))
        elif pattern and f.find(pattern) < 0:
            logger.info('Skip file not matching "%s": %s'
                        % (pattern, os.path.relpath(f_path, root)))
        else:
            logger.debug('Process Psytools file: %s'
                         % os.path.relpath(f_path, root))
            if init_processing(f_path):
                remove_psytools(f_path, root)
                insert_psytools(f_path, root)
                stop_processing(f_path)
