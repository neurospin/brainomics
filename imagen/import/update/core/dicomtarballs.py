"""Index tarballs of DICOM images.

Functions to index a tarball of DICOM images in a database or
discard from the database all data pertaining to the file.

"""
import logging
logger = logging.getLogger(__name__)

import os.path
import tarfile
import dicom


def insert_dicomtarball(filename, root):
    """Index a DICOM tarball.

    Minimal checks to avoid duplicates.

    Parameters
    ----------
    filename : str
        DICOM tarball to index.
    root : str
        Root directory of the file, to be removed for readability when
        displaying paths in messages.

    """
#>>> PLACEHOLDER
    tarball = tarfile.open(filename)
    dicom_1st_file = tarball.extractfile('./1.dcm')
    dataset = dicom.read_file(dicom_1st_file)
    if 'SeriesDescription' in dataset:
        SeriesDescription = dataset.SeriesDescription
    else:
        SeriesDescription = '?'
    logger.info('Index DICOM tarball "%s": %s'
                % (SeriesDescription, os.path.relpath(filename, root)))
#<<< PLACEHOLDER


def remove_dicomtarball(filename, root):
    """Discard data associated to a DICOM tarball.

    Discard all information originating from ``filename``.

    Parameters
    ----------
    filename : str
        DICOM tarball to discard.
    root : str
        Root directory of the file, to be removed for readability when
        displaying paths in messages.

    """
#>>> PLACEHOLDER
    logger.info('Discard DICOM image previously extracted from file: %s'
                % os.path.relpath(filename, root))
#<<< PLACEHOLDER
