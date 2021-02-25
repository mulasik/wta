import os
from os.path import expanduser

DATA_DIR = 'example_data'
INITIAL_DATA_DIR = os.path.join(DATA_DIR, 'initial_data')
VIDEO_DATA_DIR = os.path.join(DATA_DIR, 'video')
SENTENCE_EDITING_DIR = os.path.join(DATA_DIR, 'sentence_editing')

initial_xml_paths = [os.path.join(INITIAL_DATA_DIR, f) for f in os.listdir(INITIAL_DATA_DIR)
                             if os.path.isfile(os.path.join(INITIAL_DATA_DIR, f))
                             and f.endswith('idfx')]
initial_output_dir = os.path.join(expanduser('~'), 'wta', 'output_data', 'initial_data')

video_xml_paths = [os.path.join(VIDEO_DATA_DIR, f) for f in os.listdir(VIDEO_DATA_DIR)
                                  if os.path.isfile(os.path.join(VIDEO_DATA_DIR, f))
                                  and f.endswith('idfx')]
video_output_dir = os.path.join(expanduser('~'), 'wta', 'output_data', 'video')

sentence_editing_xml_paths = [os.path.join(SENTENCE_EDITING_DIR, f) for f in os.listdir(SENTENCE_EDITING_DIR)
                                  if os.path.isfile(os.path.join(SENTENCE_EDITING_DIR, f))
                                  and f.endswith('idfx')]
sentence_editing_output_dir = os.path.join(expanduser('~'), 'wta', 'output_data', 'sentence_editing')

# example files:

don = [os.path.join(INITIAL_DATA_DIR, 'Don_il_1.idfx')]
cerstin = [os.path.join(INITIAL_DATA_DIR, 'Cerstin_Mahlow_il_1.idfx')]
ulas = [os.path.join(INITIAL_DATA_DIR, 'Ulas_il_1.idfx')]
julia = [os.path.join(INITIAL_DATA_DIR, 'Julia_Krasselt_il_1.idfx')]
michael = [os.path.join(VIDEO_DATA_DIR, 'Michael_Piotrowski_il_1.idfx')]
philipp = [os.path.join(VIDEO_DATA_DIR, 'Philipp_Dreesen_il_1.idfx')]
andy = [os.path.join(VIDEO_DATA_DIR, 'Andy_Hediger_il_1.idfx')]

DEFAULT_PAUSE_DURATION = 2
DEFAULT_EDIT_DISTANCE = 3
DEFAULT_FILTERING = True

SINGLE_INI = {
    'xml': don,
    'output': initial_output_dir,
    'pause_duration': DEFAULT_PAUSE_DURATION,
    'edit_distance': DEFAULT_EDIT_DISTANCE,
    'filtering': DEFAULT_FILTERING
}

SINGLE_VIDEO = {
    'xml': michael,
    'output': video_output_dir,
    'pause_duration': DEFAULT_PAUSE_DURATION,
    'edit_distance': DEFAULT_EDIT_DISTANCE,
    'filtering': DEFAULT_FILTERING
}

INITIAL = {
    'xml': initial_xml_paths,
    'output': initial_output_dir,
    'pause_duration': DEFAULT_PAUSE_DURATION,
    'edit_distance': DEFAULT_EDIT_DISTANCE,
    'filtering': DEFAULT_FILTERING
}

VIDEO = {
    'xml': video_xml_paths,
    'output': video_output_dir,
    'pause_duration': DEFAULT_PAUSE_DURATION,
    'edit_distance': DEFAULT_EDIT_DISTANCE,
    'filtering': DEFAULT_FILTERING
}

SENTENCE_EDITING = {
    'xml': sentence_editing_xml_paths,
    'output': sentence_editing_output_dir,
    'pause_duration': DEFAULT_PAUSE_DURATION,
    'edit_distance': DEFAULT_EDIT_DISTANCE,
    'filtering': DEFAULT_FILTERING
}

