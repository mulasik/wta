class Action:
    """
    A class to represent action taken when producing text.
    Actions are derived from events.
    There are 7 types of actions:
    - Append: producing a char at the end of the text
    - Insertion: inserting a char in the middle of the text
    - Navigation: navigating through the text without producing any chars
    - Deletion: deleting a char at the end of the text
    - Midletion: deleting a char in the middle of the text
    - Replacement: marking a text segment and replacing it with a char or empty seq
    - Pasting: pasting a text segment
    """

    def __init__(
        self, content: str, startpos: int, endpos: int | None
    ) -> None:
        self.content = content
        self.startpos = startpos
        self.endpos = endpos


class KeyboardAction(Action):
    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        keyname: str,
        starttime: float,
        endtime: float,
        preceding_pause: float,
        textlen: int,
    ) -> None:
        super().__init__(content, startpos, endpos)
        self.textlen = textlen
        self.keyname = keyname
        self.starttime = starttime
        self.endtime = endtime
        self.preceding_pause = preceding_pause


class Append(KeyboardAction):
    pass


class Insertion(KeyboardAction):
    pass


class Navigation(KeyboardAction):
    pass


class Deletion(KeyboardAction):
    pass


class Midletion(KeyboardAction):
    pass


class Replacement(Action):
    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        rplcmt_endpos: int,
        rplcmt_textlen: int,
    ) -> None:
        super().__init__(content, startpos, endpos)
        self.rplcmt_textlen = rplcmt_textlen
        self.rplcmt_endpos = rplcmt_endpos


class Pasting(Action):
    def __init__(
        self, content: str, startpos: int, endpos: int | None
    ) -> None:
        super().__init__(content, startpos, endpos)
