"""Index *raw package*.

Functions to index a *raw package* file in a database.

"""
import logging
logger = logging.getLogger(__name__)

import os.path


def insert_raw(filename, root):
    """Index a *raw package*.

    First check whether ``filename`` has already been indexed in the database.
    Skip if it has already been indexed.

    Parameters
    ----------
    filename : str
        Raw package to index.
    root : str
        Root directory of the file, to be removed for readability when
        displaying paths in messages.

    """
#>>> PLACEHOLDER
    logger.info('Index raw package: %s' % os.path.relpath(filename, root))
#<<< PLACEHOLDER
