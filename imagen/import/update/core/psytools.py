"""Index Psytools files.

Functions to index a Psytools file in a database or
discard from the database all data pertaining to the file.

"""
import logging
logger = logging.getLogger(__name__)

import os.path


def insert_psytools(filename, root):
    """Index a Psytools file.

    Minimal checks to avoid duplicates.

    Parameters
    ----------
    filename : str
        Psytools file to index.
    root : str
        Root directory of the file, to be removed for readability when
        displaying paths in messages.

    """
#>>> PLACEHOLDER
    logger.info('Index Psytools file: %s' % os.path.relpath(filename, root))
#<<< PLACEHOLDER


def remove_psytools(filename, root):
    """Discard data associated to a Psytools file.

    Discard all information originating from ``filename``.

    Parameters
    ----------
    filename : str
        Psytools file to discard.
    root : str
        Root directory of the file, to be removed for readability when
        displaying paths in messages.

    """
#>>> PLACEHOLDER
    logger.info('Discard Psytools data previously extracted from file: %s'
                % os.path.relpath(filename, root))
#<<< PLACEHOLDER
