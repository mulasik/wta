import os
from os.path import expanduser

DATA_DIR = 'example_data'
VIDEO_DATA_DIR = os.path.join(DATA_DIR, 'video')

DEFAULT_PAUSE_DURATION = 2
DEFAULT_EDIT_DISTANCE = 3
DEFAULT_FILTERING = True
DEFAULT_LANGUAGE = 'German'

VIDEO = {
    'xml': [os.path.join(VIDEO_DATA_DIR, f) for f in os.listdir(VIDEO_DATA_DIR) if os.path.isfile(os.path.join(VIDEO_DATA_DIR, f)) and f.endswith('idfx')],
    'output': os.path.join(expanduser('~'), 'wta', 'output_data', 'video'),
    'pause_duration': DEFAULT_PAUSE_DURATION,
    'edit_distance': DEFAULT_EDIT_DISTANCE,
    'filtering': DEFAULT_FILTERING,
    'language': DEFAULT_LANGUAGE
}

