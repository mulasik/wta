from typing import ClassVar

# PREPROCESSING:

class KeyNames:
    RETURN = "VK_RETURN"
    TAB = "VK_TAB"
    QUOTE = "VK_OEM_7"
    CAPITAL = "VK_CAPITAL"
    BACKSPACE = "VK_BACK"
    DELETE = "VK_DELETE"
    DELETION_KEYS: ClassVar[list[str]] = [BACKSPACE, DELETE]
    END = "VK_END"
    ARROW_KEYS: ClassVar[list[str]] = ["VK_LEFT", "VK_RIGHT", "VK_UP", "VK_DOWN"]
    SHIFT_KEYS: ClassVar[list[str]] = ["VK_SHIFT", "VK_LSHIFT", "VK_RSHIFT"]
    NAVIGATION_KEYS: ClassVar[list[str]] = [END, *ARROW_KEYS]
    NON_PRODUCTION_KEYS: ClassVar[list[str]] = [*NAVIGATION_KEYS, *DELETION_KEYS, *SHIFT_KEYS]
    ERRONEOUS = "VK_ERR"


class EventTypes:
    PKE = "ProductionKeyboardEvent"
    BDKE = "BDeletionKeyboardEvent"
    DDKE = "DDeletionKeyboardEvent"
    NKE = "NavigationKeyboardEvent"
    RE = "ReplacementEvent"
    IE = "InsertEvent"

class ActionTypes:
    APP = "Append"
    INS = "Insertion"
    NAV = "Navigation"
    DEL = "Deletion"
    MID = "Midletion"
    REPL = "Replacement"
    PAST = "Pasting"

# TRANSFORMATION LAYER & PROJECTION

class TSLabels:
    APP = "append"
    INS = "insertion"
    NAV = "navigation"
    DEL = "deletion"
    MID = "midletion"
    REPL = "replacement"
    PAST = "pasting"


class TUTypes:
    SIN = "sentence interspace"
    SEC = "sentence candidate"
    SEN = "sentence"
    PIN = "paragraph interspace"

# SENTENCE LAYER & PROJECTION

class TUState:
    MOD = "modified"
    DEL = "deleted"
    NEW = "new"
    UNC_PRE = "unchanged_pre"
    UNC_POST = "unchanged_post"
    SPLIT = "split"
    MER = "merged"
    IMP: ClassVar[list[str]] = [NEW, MOD, DEL]


class SScope:
    IN_SEN = "in-sentence"
    SEN = "uni-SEN"
    SEC = "uni-SEC"
    CROSS_SEN = "cross-sentence"
    MULTI_SEN = "multi-sentence"
    NO_SEN = "no-sentence"
    UNK = "unknown sentence scope"


class SegmentTypes:
    SEN_BEG = "sentence beginning"
    SEN_MID = "sentence middle"
    SEN_END = "sentence end"
    SEN = "whole sentence"
    SEC = "whole sentence candidate"
    UNK = "unknown segment type"
    NF = "not found"
    PIN = "pin"
    SIN = "sin"


class ProductionStages:
    PRECON = "pre-contextual"
    CON = "contextual"


class OperationTypes:
    PROD = "production"
    PRECON_DEL = "pre-contextual_deletion"
    PRECON_INS = "pre-contextual_insertion"
    PRECON_REPL = "pre-contextual_replacement"
    CON_DEL = "contextual_deletion"
    CON_INS = "contextual_insertion"
    CON_REPL = "contextual_replacement"
    NON = "no-operation"

# BURST LAYER & PROJECTION

class BScope:
    # burst is a pause burst
    IN_PBURST = "in-pburst"
    UNI_PBURST = "uni-pburst"
    CROSS_PBURST = "cross-pburst"
    MULTI_PBURST = "multi-pburst"
    NO_PBURST = "no pburst"
    UNK = "unknown burst scope"


class BurstTypes:
    PP_BURST = "PP-burst"
    PR_BURST = "PR-burst"
    RP_BURST = "RP-burst"
    RR_BURST = "RR-burst"
    UNK = "unknown burst type"

# OTHER

class PointOfInscription:
    END = "text_end"
    MID = "text_middle"

