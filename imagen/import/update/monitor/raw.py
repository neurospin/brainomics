"""Index *raw packages*.

*Raw packages* contain DICOM images and associated data transmitted from
the acquisition centres through the SCITO channel. They are typically
submitted to directory ``/neurospin/imagen/FU2/RAW/PSC2``.

A subject may have more than one *raw package*. They will differ by their
timestamp. All successive raw packages associated to a subject are kept
on disk and need to be indexed in the database. Note however that only the
latest raw package will be further processed at NeuroSpin and the results
indexed in the database.

Since the source of this data is not under our control, it makes sense
to continuously monitor ``/neurospin/imagen/FU2/RAW/PSC2`` and check
for updated files. This is performed by ``monitor_raw()``.

"""
import logging
logger = logging.getLogger(__name__)

import os
import datetime
import re


__SKIP_CENTRE_DIR = {
    'dawba',
    'genetic',
    'psytools',
    'QC',
    'recruitment',
}

__REGEX_RAW = re.compile('(\d{12})_(\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2})'
                         '.0.tar.gz')


def monitor_raw(root):
    """Index *raw packages* within a directory.

    The expected tree structure of the directory is
    ``<centre>/<subject>_<date_time>.0.tar.gz``.

    Parameters
    ----------
    root : str
        Directory to explore.

    """
    for centre in os.listdir(root):
        centre_dir = os.path.join(root, centre)
        if centre in __SKIP_CENTRE_DIR:
            logger.info('Skip directory: %s' % centre)
        elif os.path.isdir(centre_dir):
            logger.info('Process centre: %s' % centre)
            monitor_centre(centre_dir, root)
        else:
            logger.info('Skip unexpected file: %s' % centre)


from update.core.raw import insert_raw

from update.history import init_processing
from update.history import stop_processing


def monitor_centre(centre_dir, root):
    """Index *raw packages* within a centre subdirectory.

    The subdirectory is expected to contain ``<subject>_<date_time>.0.tar.gz``
    tarballs.

    Parameters
    ----------
    centre_dir : str
        Directory to explore.
    root : str
        Root directory of the data, to be removed for readability when
        displaying paths in messages.

    See Also
    --------
    monitor_raw

    """
    for f in os.listdir(centre_dir):
        f_path = os.path.join(centre_dir, f)
        match = __REGEX_RAW.match(f)
        if match:
            logger.debug('Process raw package: %s'
                         % os.path.relpath(f_path, root))
            f_timestamp = os.path.getmtime(f_path)
            f_timestamp = datetime.datetime.fromtimestamp(f_timestamp)
            subject = match.groups()[0]
            timestamp = datetime.datetime.strptime(match.groups()[1],
                                                   '%Y-%m-%d_%H:%M:%S')
            if f_timestamp < timestamp:
                logger.warn('File system timestamp is not consistent with'
                            ' filename timestamp: %s'
                            % os.path.relpath(f_path, root))
            if init_processing(f_path):
                insert_raw(f_path, root)
                stop_processing(f_path)
        else:
            logger.warn('Skip file with unexpected filename: %s'
                        % os.path.relpath(f_path, root))
