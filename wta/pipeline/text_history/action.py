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

    def __init__(self, content, startpos, endpos):
        self.content = content
        self.startpos = startpos
        self.endpos = endpos


class Append(Action):

    def __init__(self, content, startpos, endpos, keyname, starttime, endtime, pause):
        super().__init__(content, startpos, endpos)
        self.keyname = keyname
        self.starttime = starttime
        self.endtime = endtime
        self.pause = pause


class Insertion(Action):

    def __init__(self, content, startpos, endpos, keyname, starttime, endtime, pause):
        super().__init__(content, startpos, endpos)
        self.keyname = keyname
        self.starttime = starttime
        self.endtime = endtime
        self.pause = pause


class Navigation(Action):

    def __init__(self, content, startpos, endpos, keyname, starttime, endtime, pause):
        super().__init__(content, startpos, endpos)
        self.keyname = keyname
        self.starttime = starttime
        self.endtime = endtime
        self.pause = pause


class Deletion(Action):

    def __init__(self, content, startpos, endpos, keyname, starttime, endtime, pause):
        super().__init__(content, startpos, endpos)
        self.keyname = keyname
        self.starttime = starttime
        self.endtime = endtime
        self.pause = pause


class Midletion(Action):

    def __init__(self, content, startpos, endpos, keyname, starttime, endtime, pause):
        super().__init__(content, startpos, endpos)
        self.keyname = keyname
        self.starttime = starttime
        self.endtime = endtime
        self.pause = pause


class Replacement(Action):

    def __init__(self, content, startpos, endpos, rplcmt_endpos):
        super().__init__(content, startpos, endpos)
        self.rplcmt_endpos = rplcmt_endpos


class Pasting(Action):

    def __init__(self, content, startpos, endpos):
        super().__init__(content, startpos, endpos)


