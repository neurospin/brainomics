"""Explore the ```` directory."""
import logging
logger = logging.getLogger(__name__)

import os.path


def walk_spmstatsintra(root):
    """
    Explore a directory tree containing images and statistics genrated by SPM.

    The data is to be found in files in ``<subject>/<session>/<series>/``.

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


STATS_KEYS = (
    ('rpv', 'RPV.nii.gz'),
    ('resms', 'ResMS.nii.gz'),
    ('statsintra_mat', 'SPM.mat.gz'),
    ('job_statsintra', 'job_spmstatsintra_%s_%s.m'),
    ('mask', 'mask.nii.gz'),
    ('rpl_a', 'rpL_a%s*.txt'),
    ('beta', 'beta_*.nii.gz'),
    ('con', 'con_*.nii.gz'),
    ('ess', 'ess_*.nii.gz'),
    ('spmf', 'spmF_*.nii.gz'),
    ('spmt', 'spmT_*.nii.gz'),
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
    series = os.path.basename(series_dir)
    session_dir = os.path.dirname(series_dir)
    subject_dir = os.path.dirname(session_dir)
    subject = os.path.basename(subject_dir)

    # prepare file names
    stats_keys = []
    for key in STATS_KEYS:
        if key[0] == 'job_statsintra':
            key1 = key[1] % (series.replace('_', ''), subject)
            stats_keys.append((key[0], key1))
        elif key[0] == 'rpl_a':
            stats_keys.append((key[0], key[1] % subject))
        stats_keys.append((key[0], key[1]))

    for key in stats_keys:
        for stats_path in glob.glob(os.path.join(series_dir, 'swea', key[1])):
            if os.path.isfile(stats_path):
                logger.debug('Processing preprocessed SPM stats file: %s' %
                             os.path.relpath(stats_path, root))
                if init_processing(stats_path):
#>>> PLACEHOLDER
                    pass
#<<< PLACEHOLDER
                    stop_processing(stats_path)
                else:
                    pass ###################################
