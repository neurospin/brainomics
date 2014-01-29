"""Explore the ``spmpreproc`` directory."""
import logging
logger = logging.getLogger(__name__)

import os.path


def walk_spmpreproc(root):
    """
    Explore a directory tree containing images preprocessed by SPM.

    The directory tree must be organized this way:
    * MRI images are in subdirectories ``<subject>/mprage/``,
    * fMRI images are in subdirectories ``<subject>/<session>/<series>/``,

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
            logger.info('Processing subject: %s' %
                        subject)
            walk_subject(subject_dir, root)
        else:
            logger.warn('Skipping unexpected file: %s' % subject)


def walk_subject(subject_dir, root):
    """
    Explore a subject directory.

    A subject directory contains subdirectories ``<session>/<series>/``
    where the name of ``<session>`` is typically ``SessionA`` or
    ``SessionB``.

    Parameters
    ----------
    subject_dir : str
        Directory to explore.
    root : str
        Root directory of the data, to be removed for readability when
        displaying paths in messages.

    See Also
    --------
    process_mprage, walk_session

    """
    for session in os.listdir(subject_dir):
        session_dir = os.path.join(subject_dir, session)
        session_rel = os.path.relpath(session_dir, root)
        if os.path.isdir(session_dir):
            if session == 'mprage':
                logger.debug('Processing preprocessed MP RAGE series: %s' %
                             session_rel)
                process_mprage(session_dir, root)
            else:
                logger.debug('Processing session: %s' % session_rel)
                walk_session(session_dir, root)
        else:
            logger.warn('Skipping unexpected file: %s' % session_rel)


def walk_session(session_dir, root):
    """
    Explore a session directory.

    A session directory contains subdirectories ``<series>/``.

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


from update.history import init_processing
from update.history import stop_processing

import glob


MPRAGE_KEYS_1 = (
    'y_mprage',
    'mmprage',
    'wmmprage',
)

MPRAGE_KEYS_2 = (
    'c',
    'mwc',
    'wc',
)


def process_mprage(mprage_dir, root):
    """
    ###

    """
    # extract subject name from path - for consistency checks on file names
    subject_dir = os.path.dirname(mprage_dir)
    subject = os.path.basename(subject_dir)

    for key in MPRAGE_KEYS_1:
        mprage = key + subject + '.nii.gz'
        mprage_path = os.path.join(mprage_dir, mprage)
        if os.path.isfile(mprage_path):
            logger.debug('Processing preprocessed MP RAGE file: %s' %
                         os.path.relpath(mprage_path, root))
            if init_processing(mprage_path):
#>>> PLACEHOLDER
                pass
#<<< PLACEHOLDER
                stop_processing(mprage_path)

    for key in MPRAGE_KEYS_2:
        mprage_glob = key + '?' + subject + '*.nii.gz'
        for mprage_path in glob.glob(os.path.join(mprage_dir, mprage_glob)):
            if os.path.isfile(mprage_path):
                logger.debug('Processing preprocessed MP RAGE file: %s' %
                             os.path.relpath(mprage_path, root))
                if init_processing(mprage_path):
#>>> PLACEHOLDER
                    pass
#<<< PLACEHOLDER
                    stop_processing(mprage_path)


FMRI_KEYS = (
    'meana',
    'wmeana',
    'wea',
    'wa',
    'weamask',
    'wamask',
)


def process_series(series_dir, root):
    """
    Process a series directory.

    Parameters
    ----------
    series_dir : str
        Directory to process.
    root : str
        Root directory of the data, to be removed for readability when
        displaying paths in messages.

    """
    # extract subject name from path - for consistency checks on file names
    session_dir = os.path.dirname(series_dir)
    subject_dir = os.path.dirname(session_dir)
    subject = os.path.basename(subject_dir)

    for key in FMRI_KEYS:
        fmri_glob = key + subject + '*.nii.gz'
        for fmri_path in glob.glob(os.path.join(series_dir, fmri_glob)):
            if os.path.isfile(fmri_path):
                logger.debug('Processing preprocessed fMRI file: %s' %
                             os.path.relpath(fmri_path, root))
                if init_processing(fmri_path):
#>>> PLACEHOLDER
                    pass
#<<< PLACEHOLDER
                    stop_processing(fmri_path)
