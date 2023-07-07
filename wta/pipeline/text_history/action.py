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

    def __init__(self, content: str, startpos: int, endpos: int | None, textlen: int) -> None:
        self.content = content
        self.startpos = startpos
        self.endpos = endpos
        self.textlen = textlen


class KeyboardAction(Action):
    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        keyname: str,
        starttime: int,
        endtime: int,
        pause: int | None,
        textlen: int,
    ) -> None:
        super().__init__(content, startpos, endpos, textlen)
        self.keyname = keyname
        self.starttime = starttime
        self.endtime = endtime
        self.pause = pause


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
        super().__init__(content, startpos, endpos, rplcmt_textlen)
        self.rplcmt_endpos = rplcmt_endpos


class Pasting(Action):
    def __init__(
        self, content: str, startpos: int, endpos: int | None, textlen: int
    ) -> None:
        super().__init__(content, startpos, endpos, textlen)
