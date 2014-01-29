"""Copied from:
``/neurospin/imagen/src/scripts/indexation/fmri_csvs_infos.py``

Written in 2009 by Alexis Barbot.

"""


csv_attr = {
    'ss': {
        'name': 'STOP_SIGNAL_TASK task',
        'xml_name': 'Stop_signal_task',
        'minimal': 'stop',
        'column_nb': 17,
        'attr': {
            0: 'id',
            1: 'trial_category',
            2: 'trial_start_time',
            3: 'pre-determined_onset',
            4: 'go_stimulus_presentation_time',
            5: 'stimulus_presented',
#            6: 'theoretical_delay',
            6: 'delay',
            7: 'stop_stimulus_presentation_time',
            8: 'response_made_by_subject',
            9: 'absolute_response_time',
            10: 'relative_response_time',
            11: 'response_outcome',
            12: 'real_jitter',
            13: 'pre-determined_jitter',
            14: 'success_rate_of_variable_delay_stop_trials'
        }
    },
    'rps': {
        'name': 'REWARD_AND_PUNISHMENT_TASK task',
        'xml_name': 'rps_task',
        'minimal': 'reward',
        'column_nb': 21,
        'attr' :{
            0: 'id',
            1: 'trial_category',
            2: 'trial_start_time',
            3: 'predetermined_onset',
            4: 'anticipation_start_phase_time',
            5: 'anticipation_phase_duration',
            6: 'anticipation_stimulus_presentation_time',
            7: 'response_made_by_subject',
            8: 'response_time',
            9: 'fixation_phase_start_time',
            10: 'fixation_phase_duration',
            11: 'outcome_phase_start_time',
            12: 'outcome_phase_duration',
            13: 'outcome_stimulus_presentation_time',
            14: 'loser_card',
            15: 'winner_card',
            16: 'position_of_the_winner_card',
            17: 'amount',
            18: 'isi'
        }
    },
    'cga': {
        'name': 'GLOBAL_COGNITIVE_ASSESSMENT_TASK task',
        'xml_name': 'gca',
        'minimal': 'global',
        'column_nb': 9,
        'attr': {
            0: 'id',
            1: 'trial_category',
            2: 'trial_start_time',
            3: 'predetermined_onset',
            4: 'stimulus_presented',
            5: 'stimulus_presentation_time',
            6: 'response_made_by_subject',
            7: 'predetermined_jitter',
            8: 'time_response_made'
        }
    },
    'ft': {
        'name': 'FACE_TASK task',
        'xml_name': 'Face_task',
        'minimal': 'faces',
        'column_nb': 2,
        'attr': {
            0: 'trial_start_time',
            1: 'video_clip_name'
        }
    },
    'mid': {
        'name': 'MID_TASK task',
        'xml_name': 'MID_task',
        'minimal': 'MID',
        'column_nb': 17,
        'attr': {
            0:'id',
            1: 'trial_category',
            2: 'trial_start_time',
            3: 'predetermined_onset',
            4: 'cue_presented',
            5: 'anticipation_start_phase_time',
            6: 'anticipation_phase_duration',
            7: 'target_phase_start_time',
            8: 'target_phase_duration',
            9: 'response_made_by_subject',
            10: 'response_time',
            11: 'feedback_phase_start_time',
            12: 'outcome',
            13: 'amount',
            14: 'fixation_phase_start_time',
            15: 'success_rate',
            16: 'scanner_pulse'
        }
    },
    'recog': {
        'name': 'RECOGNITION_TASK task',
        'xml_name': 'Recognition_task',
        'minimal': 'faces',
        'column_nb': 3,
        'attr': {
            0: 'TimePassed',
            1: 'UserResponse',
            2: 'ImageFileName'
        }
    }
}
