class KeyNames:
    BACKSPACE = 'VK_BACK'
    DELETE = 'VK_DELETE'
    DELETION_KEYS = [BACKSPACE, DELETE]
    END = 'VK_END'
    ARROW_KEYS = ['VK_LEFT', 'VK_RIGHT', 'VK_UP', 'VK_DOWN']
    NAVIGATION_KEYS = [END, *ARROW_KEYS]
    NON_PRODUCTION_KEYS = [*NAVIGATION_KEYS, *DELETION_KEYS]


class EventTypes:
    PKE = 'ProductionKeyboardEvent'
    BDKE = 'BDeletionKeyboardEvent'
    DDKE = 'DDeletionKeyboardEvent'
    NKE = 'NavigationKeyboardEvent'
    RE = 'ReplacementEvent'
    IE = 'InsertEvent'


class EventCategories:
    PRE_DEL = 'before deletion'
    POST_DEL = 'after deletion'
    PRE_INS = 'before insertion'
    POST_INS = 'after insertion'
    PRE_REPL = 'before replacement'
    POST_REPL = 'after replacement'
    END = 'navigating to end'
    NAV = 'navigating without editing'
    FINAL = 'final text revision'

