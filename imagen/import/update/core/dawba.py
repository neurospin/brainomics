"""Index DAWBA files.

Functions to index a DAWBA file in a database or
discard from the database all data pertaining to the file.

"""
import logging
logger = logging.getLogger(__name__)

import os.path


def insert_dawba(filename, root):
    """Index a DAWBA file.

    Minimal checks to avoid duplicates.

    Parameters
    ----------
    filename : str
        DAWBA file to index.
    root : str
        Root directory of the file, to be removed for readability when
        displaying paths in messages.

    """
#>>> PLACEHOLDER
    logger.info('Index DAWBA file: %s' % os.path.relpath(filename, root))
#<<< PLACEHOLDER


def remove_dawba(filename, root):
    """Discard data associated to a DAWBA file.

    Discard all information originating from ``filename``.

    Parameters
    ----------
    filename : str
        DAWBA file to discard.
    root : str
        Root directory of the file, to be removed for readability when
        displaying paths in messages.

    """
#>>> PLACEHOLDER
    logger.info('Discard DAWBA data previously extracted from file: %s'
                % os.path.relpath(filename, root))
#<<< PLACEHOLDER
