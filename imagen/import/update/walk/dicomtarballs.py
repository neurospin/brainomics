"""Index DICOM tarballs.

DICOM tarballs are typically found in
``/neurospin/imagen/FU2/processed/dicomtarballs``.

We are in control of the process that produces the DICOM tarballs.
We can therefore manually start the process of indexing. This module
does only minimally check for duplicates. It can be used for the
initial import of a directory.

"""
import logging
logger = logging.getLogger(__name__)

import os


def walk_dicomtarballs(root):
    """Index DICOM tarballs within a top-level directory.

    Each DICOM tarball comes with a dump of the header of one of the DICOM
    files in the tarball:
    * ``<subject>/<session>/<series>/<series>.dcmheader.txt``,
    * ``<subject>/<session>/<series>/<series>.tar.gz``.
    We only process the DICOM tarball itself.

    Parameters
    ----------
    root : str
        Directory to explore.

    See Also
    --------
    walk_subject

    """
    for subject in os.listdir(root):
        subject_dir = os.path.join(root, subject)
        if os.path.isdir(subject_dir):
            logger.info('Processing subject: %s' % subject)
            walk_subject(subject_dir, root)
        else:
            logger.warn('Skipping unexpected file: %s' % subject)


def walk_subject(subject_dir, root):
    """
    Explore a subject directory.

    A subject directory contains session subdirectories, typically ``SessionA``.

    Parameters
    ----------
    subject_dir : str
        Directory to explore.
    root : str
        Root directory of the data, to be removed for readability when
        displaying paths in messages.

    See Also
    --------
    walk_session

    """
    for session in os.listdir(subject_dir):
        session_dir = os.path.join(subject_dir, session)
        session_rel = os.path.relpath(session_dir, root)
        if os.path.isdir(session_dir):
            logger.debug('Processing session: %s' % session_rel)
            walk_session(session_dir, root)
        else:
            logger.warn('Skipping unexpected file: %s' % session_rel)


def walk_session(session_dir, root):
    """
    Explore a session directory.

    A session directory contains a subdirectory for each DICOM series.

    Parameters
    ----------
    session_dir : str
        Directory to explore.
    root : str
        Root directory of the data, to be removed for readability when
        displaying paths in messages.

    See Also
    --------
    process_series

    """
    for series in os.listdir(session_dir):
        series_dir = os.path.join(session_dir, series)
        series_rel = os.path.relpath(series_dir, root)
        if os.path.isdir(series_dir):
            logger.debug('Processing series: %s' % series_rel)
            process_series(series_dir, root)
        else:
            logger.warn('Skipping unexpected file: %s' % series_rel)


from update.core.dicomtarballs import insert_dicomtarball
from update.core.dicomtarballs import remove_dicomtarball


from update.history import init_processing
from update.history import stop_processing


def process_series(series_dir, root):
    """
    Process a series directory.

    A series directory contains:
    * tarballs containing DICOM files,
    * for each tarball, the dump of the header of one of the DICOM files.

    DICOM tarballs are processed. Dumps of DICOM file headers are skipped.
    If needed, open up DICOM tarballs and directly read the contents of
    DICOM file headers.

    Parameters
    ----------
    series_dir : str
        Directory to process.
    root : str
        Root directory of the data, to be removed for readability when
        displaying paths in messages.

    """
    series = os.path.basename(series_dir)
    for f in os.listdir(series_dir):
        f_path = os.path.join(series_dir, f)
        if os.path.isfile(f_path):
            if f == series + '.dcmheader.txt':
                logger.debug('Skip DICOM header dump: %s' %
                             os.path.relpath(f_path, root))
            elif f == series + '.tar.gz':
                logger.info('Process DICOM tarball: %s' %
                             os.path.relpath(f_path, root))
                if init_processing(f_path):
                    remove_dicomtarball(f_path, root)
                    insert_dicomtarball(f_path, root)
                    stop_processing(f_path)
            else:
                logger.warn('Skip unexpected file: %s' %
                             os.path.relpath(f_path, root))
