import os
from os.path import expanduser

DATA_DIR = "example_data"
VIDEO_DATA_DIR = os.path.join(DATA_DIR, "video")

DEFAULT_PAUSE_DURATION = 2
DEFAULT_EDIT_DISTANCE = 3
DEFAULT_FILTERING = True
DEFAULT_LANGUAGE = "German"

VIDEO = {
    "xml": [
        os.path.join(VIDEO_DATA_DIR, f)
        for f in os.listdir(VIDEO_DATA_DIR)
        if os.path.isfile(os.path.join(VIDEO_DATA_DIR, f)) and f.endswith("idfx")
    ],
    "output": os.path.join("output_data", "video"),
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "edit_distance": DEFAULT_EDIT_DISTANCE,
    "filtering": DEFAULT_FILTERING,
    "language": DEFAULT_LANGUAGE,
}

GREEK_DATA_DIR = os.path.join(DATA_DIR, "greek")
GREEK = {
    "xml": [
        os.path.join(GREEK_DATA_DIR, f)
        for f in os.listdir(GREEK_DATA_DIR)
        if os.path.isfile(os.path.join(GREEK_DATA_DIR, f)) and f.endswith("idfx")
    ],
    "output": os.path.join("output_data", "greek"),
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "edit_distance": DEFAULT_EDIT_DISTANCE,
    "filtering": DEFAULT_FILTERING,
    "language": "Greek",
}

GREEK_PHASE1_DATA_DIR = os.path.join(DATA_DIR, "Rohdaten", "Phase-1")
GREEK_PHASE1 = {
    "xml": [
        os.path.join(GREEK_PHASE1_DATA_DIR, f)
        for f in os.listdir(GREEK_PHASE1_DATA_DIR)
        if os.path.isfile(os.path.join(GREEK_PHASE1_DATA_DIR, f)) and f.endswith("idfx")
    ],
    "output": os.path.join("output_data", "Processed", "Phase-1"),
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "edit_distance": DEFAULT_EDIT_DISTANCE,
    "filtering": DEFAULT_FILTERING,
    "language": "Greek",
}

GREEK_PHASE2_DATA_DIR = os.path.join(DATA_DIR, "Rohdaten", "Phase-2")
GREEK_PHASE2 = {
    "xml": [
        os.path.join(GREEK_PHASE2_DATA_DIR, f)
        for f in os.listdir(GREEK_PHASE2_DATA_DIR)
        if os.path.isfile(os.path.join(GREEK_PHASE2_DATA_DIR, f)) and f.endswith("idfx")
    ],
    "output": os.path.join("output_data", "Processed", "Phase-2"),
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "edit_distance": DEFAULT_EDIT_DISTANCE,
    "filtering": DEFAULT_FILTERING,
    "language": "Greek",
}

GREEK_PHASE3_TASK0_DATA_DIR = os.path.join(DATA_DIR, "Rohdaten", "Phase-3", "Task0-IDFX")
GREEK_PHASE3_TASK0 = {
    "xml": [
        os.path.join(GREEK_PHASE3_TASK0_DATA_DIR, f)
        for f in os.listdir(GREEK_PHASE3_TASK0_DATA_DIR)
        if os.path.isfile(os.path.join(GREEK_PHASE3_TASK0_DATA_DIR, f)) and f.endswith("idfx")
    ],
    "output": os.path.join("output_data", "Processed", "Phase-3", "Task0-IDFX"),
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "edit_distance": DEFAULT_EDIT_DISTANCE,
    "filtering": DEFAULT_FILTERING,
    "language": "Greek",
}

GREEK_PHASE3_TASK1_DATA_DIR = os.path.join(DATA_DIR, "Rohdaten", "Phase-3", "Task1-IDFX")
GREEK_PHASE3_TASK1 = {
    "xml": [
        os.path.join(GREEK_PHASE3_TASK1_DATA_DIR, f)
        for f in os.listdir(GREEK_PHASE3_TASK1_DATA_DIR)
        if os.path.isfile(os.path.join(GREEK_PHASE3_TASK1_DATA_DIR, f)) and f.endswith("idfx")
    ],
    "output": os.path.join("output_data", "Processed", "Phase-3", "Task1-IDFX"),
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "edit_distance": DEFAULT_EDIT_DISTANCE,
    "filtering": DEFAULT_FILTERING,
    "language": "Greek",
}

GREEK_PHASE3_TASK2_DATA_DIR = os.path.join(DATA_DIR, "Rohdaten", "Phase-3", "Task2-IDFX")
GREEK_PHASE3_TASK2 = {
    "xml": [
        os.path.join(GREEK_PHASE3_TASK2_DATA_DIR, f)
        for f in os.listdir(GREEK_PHASE3_TASK2_DATA_DIR)
        if os.path.isfile(os.path.join(GREEK_PHASE3_TASK2_DATA_DIR, f)) and f.endswith("idfx")
    ],
    "output": os.path.join("output_data", "Processed", "Phase-3", "Task2-IDFX"),
    "pause_duration": DEFAULT_PAUSE_DURATION,
    "edit_distance": DEFAULT_EDIT_DISTANCE,
    "filtering": DEFAULT_FILTERING,
    "language": "Greek",
}
