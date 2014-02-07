"""Explore the ``nifti`` directory."""
import logging
logger = logging.getLogger(__name__)

import os


def walk_nifti(root):
    """
    Explore a directory tree containing NIfTI files.

    The directory tree must be organized this way:
    * subdirectories ``<subject>/<session>/<series>/``
    * each leaf subdirectory contains:
    ** NIfTI "base" files <subject>*.nii.gz, to be referenced
    ** additional NIfTI files for anatomical MRI, not to be referenced:
    *** o<subject>*.nii.gz
    *** co<subject>*.nii.gz
    ** additional BVAL/BVEC files for DTI, to be referenced:
    *** <subject>*.bval
    *** <subject>*.bvec

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

    A subject directory contains:
    * session subdirectories typically called ``SessionA`` that contain
      the NIfTI files,
    * a subdirectory ``BehaviouralData`` that contains additional data.

    Parameters
    ----------
    subject_dir : str
        Directory to explore.
    root : str
        Root directory of the data, to be removed for readability when
        displaying paths in messages.

    See Also
    --------
    process_behavioural_data, walk_session

    """
    for session in os.listdir(subject_dir):
        session_dir = os.path.join(subject_dir, session)
        session_rel = os.path.relpath(session_dir, root)
        if os.path.isdir(session_dir):
            if session == 'BehaviouralData':
                logger.debug('Processing behavioural data: %s' % session_rel)
                process_behavioural_data(session_dir, root)
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
from update.fmri_csvs import csv_attr


def process_behavioural_data(behavioural_data_dir, root):
    """
    ###

    """
    # extract subject name from path - for consistency checks on file names
    subject_dir = os.path.dirname(behavioural_data_dir)
    subject = os.path.basename(subject_dir)

    # CANTAB files
    datasheet = 'datasheet_' + subject + ' .csv'
    datasheet_path = os.path.join(behavioural_data_dir, datasheet)
    if os.path.isfile(datasheet_path):
        logger.debug('Processing CANTAB datasheet: %s' %
                     os.path.relpath(datasheet_path, root))
        if init_processing(datasheet_path):
#>>> PLACEHOLDER
            pass
#<<< PLACEHOLDER
            stop_processing(datasheet_path)
        detailed = 'detailed_datasheet_' + subject + '.csv'
        detailed_path = os.path.join(behavioural_data_dir, detailed)
        if os.path.isfile(detailed_path):
            logger.debug('Processing CANTAB detailed datasheet: %s' %
                         os.path.relpath(detailed_path, root))
            if init_processing(detailed_path):
#>>> PLACEHOLDER
                pass
#<<< PLACEHOLDER
                stop_processing(detailed_path)
        report = 'report_' + subject + '.html'
        report_path = os.path.join(behavioural_data_dir, report)
        if os.path.isfile(report_path):
            logger.debug('Processing CANTAB detailed datasheet: %s' %
                         os.path.relpath(report_path, root))
            if init_processing(report_path):
#>>> PLACEHOLDER
                pass
#<<< PLACEHOLDER
                stop_processing(report_path)
    else:
        logger.warning('Missing CANTAB file in: %s' %
                       os.path.relpath(behavioural_data_dir, root))

    # QualityReport
    quality = 'QualityReport.csv'
    quality_path = os.path.join(behavioural_data_dir, quality)
    if os.path.isfile(quality_path):
        logger.debug('Processing Quality Report: %s' %
                     os.path.relpath(quality_path, root))
        if init_processing(quality_path):
#>>> PLACEHOLDER
            pass
#<<< PLACEHOLDER
            stop_processing(quality_path)
    else:
        logger.warning('Missing Quality Report in: %s' %
                       os.path.relpath(behavioural_data_dir, root))

    # fMRI CSVs
    for key in csv_attr.keys():
        fmri_csv = key + '_' + subject + '.csv'
        fmri_csv_path = os.path.join(behavioural_data_dir, fmri_csv)
        if os.path.isfile(fmri_csv_path):
            fmri_csv_path = os.path.join(behavioural_data_dir, fmri_csv)
            logger.debug('Processing fMRI CSV file: %s' %
                         os.path.relpath(fmri_csv_path, root))
            if init_processing(fmri_csv_path):
#>>> PLACEHOLDER
                pass
#<<< PLACEHOLDER
                stop_processing(fmri_csv_path)


import glob


def process_series(series_dir, root):
    """
    Process a series directory.

    ###

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

    base_glob = subject + '*.nii.gz'
    for base_path in glob.glob(os.path.join(series_dir, base_glob)):
        if os.path.isfile(base_path):
            logger.debug('Processing NIfTI file: %s' %
                         os.path.relpath(base_path, root))
            # DTI images also have BVAL/BVEC files
            bval_path = base_path.replace('.nii.gz', '.bval')
            if os.path.isfile(bval_path):
                logger.debug('Found BVAL file: %s' %
                             os.path.relpath(bval_path, root))
            else:
                bval_path = None
            bvec_path = base_path.replace('.nii.gz', '.bvec')
            if os.path.isfile(bvec_path):
                logger.debug('Found BVEC file: %s' %
                             os.path.relpath(bvec_path, root))
            else:
                bvec_path = None
            # OK, we have a NIfTI base file and possibly BVAL/BVEC files
            if bval_path and bvec_path:
                # we have a set of NIfTI/BVAL/BVEC files
                if init_processing(base_path, bval_path, bvec_path):
#>>> PLACEHOLDER
                    ### FileSet of NIfTI/BVAL/BVEC files
                    pass
#<<< PLACEHOLDER
                    stop_processing(base_path, bval_path, bvec_path)
            elif init_processing(base_path):
#>>> PLACEHOLDER
                ### single NIfTI file
                pass
#<<< PLACEHOLDER
                stop_processing(base_path)
