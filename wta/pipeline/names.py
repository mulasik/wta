class KeyNames:
    BACKSPACE = "VK_BACK"
    DELETE = "VK_DELETE"
    DELETION_KEYS = [BACKSPACE, DELETE]
    END = "VK_END"
    ARROW_KEYS = ["VK_LEFT", "VK_RIGHT", "VK_UP", "VK_DOWN"]
    SHIFT_KEYS = ["VK_SHIFT", "VK_LSHIFT", "VK_RSHIFT"]
    NAVIGATION_KEYS = [END, *ARROW_KEYS]
    NON_PRODUCTION_KEYS = [*NAVIGATION_KEYS, *DELETION_KEYS, *SHIFT_KEYS]


class EventTypes:
    PKE = "ProductionKeyboardEvent"
    BDKE = "BDeletionKeyboardEvent"
    DDKE = "DDeletionKeyboardEvent"
    NKE = "NavigationKeyboardEvent"
    RE = "ReplacementEvent"
    IE = "InsertEvent"


class EventCategories:
    PRE_DEL = "before deletion"
    POST_DEL = "after deletion"
    PRE_INS = "before insertion"
    POST_INS = "after insertion"
    PRE_REPL = "before replacement"
    POST_REPL = "after replacement"
    END = "navigating to end"
    NAV = "navigating without editing"
    FINAL = "final text revision"


class TSLabels:
    APP = "append"
    INS = "insertion"
    NAV = "navigation"
    DEL = "deletion"
    MID = "midletion"
    REPL = "replacement"
    PAST = "pasting"


class SenLabels:
    MOD = "modified"
    DEL = "deleted"
    NEW = "new"
    UNC_PRE = "unchanged_pre"
    UNC_POST = "unchanged_post"
    SPLIT = "split"


class TextTransScope:
    IN_SEN = "in-sentence transformation"
    SEN = "full sentence transformation"
    CROSS_SEN = "cross-sentence"
    MULTI_SEN = "multi-sentence"
    NO_SEN = "no-sentence"
    UNK = "unknown_text_trans_scope"


class SenSegmentTypes:
    SEN_BEG = "sentence_beginning"
    SEN_MID = "sentence_middle"
    SEN_END = "sentence_end"
    SEN = "full_sentence"
    UNK = "unknown_segment_type"
    PIN = "paragraph_interspace"
    SIN = "sentence_interspace"


class PointOfInscription:
    END = "text_end"
    MID = "text_middle"


class ProductionStages:
    PRECON = "pre-contextual"
    CON = "contextual"


class SenTransformationTypes:
    PROD = "production"
    PRECON_DEL = "pre-contextual_deletion"
    PRECON_INS = "pre-contextual_insertion"
    PRECON_REV = "pre-contextual_revision"
    CON_DEL = "contextual_deletion"
    CON_INS = "contextual_insertion"
    CON_REV = "contextual_revision"
