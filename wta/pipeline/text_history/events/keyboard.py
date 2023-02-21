from .base import BaseEvent
from ..action import Append, Insertion, Pasting, Navigation, Deletion, Midletion
from wta.pipeline.names import EventTypes

CHAR_NUMBER_DIFF_PRODUCTION = 1
CHAR_NUMBER_DIFF_DDELETION = 1
# Document length in the idfx file == position + 1.
# In case of backspace deletion the startpos == startpos - 1 because this is where the char actually gets deleted.
# So the total diff is 2 between the position of the deleted char and the document length provided in idfx.
CHAR_NUMBER_DIFF_BDELETION = 2


class KeyboardEvent(BaseEvent):
    """
    A class to represent the keyboard event.
    Keyboard event is an event type stored in the idfx file.
    Keyboard event consists in pressing a key in order to:
        - type a character
        - remove a character
        - navigate in text without editing
    Exmaple from idfx file:
    <event id="3" type="keyboard">
        <part type="wordlog">
            <position>332</position>
            <documentLength>333</documentLength>
            <replay>True</replay>
        </part>
        <part type="winlog">
            <startTime>111125390</startTime>
            <endTime>111125395</endTime>
            <key>VK_B</key>
            <value>B</value>
            <keyboardstate></keyboardstate>
        </part>
    </event>
    """

    def __init__(self, content, startpos, endpos, keyname, starttime, endtime, textlen):
        super().__init__(content, startpos, endpos)
        self.keyname = keyname
        self.starttime = starttime
        self.endtime = endtime
        self.textlen = textlen
        self.pause = None

    def set_pause(self):
        try:
            self.pause = (self.starttime - self.prev_evnt.starttime) / 1000
        except TypeError:
            self.pause = None
        except AttributeError:
            self.pause = None


class ProductionKeyboardEvent(KeyboardEvent):
    def __init__(self, content, startpos, endpos, keyname, starttime, endtime, textlen):
        super().__init__(
            content, startpos, endpos, keyname, starttime, endtime, textlen
        )
        self.char_number_diff = CHAR_NUMBER_DIFF_PRODUCTION

    def to_action(self):
        cur_textlen = self.textlen - self.char_number_diff
        # if the next event is a replacement, the keyboard event is part of the replacement
        if type(self.next_evnt).__name__ == EventTypes.RE:
            pass
        # if more than 1 character has been produced at one go, the action is pasting
        elif len(self.content) > 1:
            return Pasting(self.content, self.startpos, self.endpos)
        # if position is smaller then text length
        elif len(self.content) == 1 and self.startpos < cur_textlen:
            return Insertion(
                self.content,
                self.startpos,
                self.endpos,
                self.keyname,
                self.starttime,
                self.endtime,
                self.pause,
                cur_textlen,
            )
        else:
            return Append(
                self.content,
                self.startpos,
                self.endpos,
                self.keyname,
                self.starttime,
                self.endtime,
                self.pause,
                cur_textlen,
            )


class DeletionKeyboardEvent(KeyboardEvent):
    def __init__(self, content, startpos, endpos, keyname, starttime, endtime, textlen):
        super().__init__(
            content, startpos, endpos, keyname, starttime, endtime, textlen
        )

    def to_action(self):
        cur_textlen = self.textlen - self.char_number_diff
        if type(self.next_evnt).__name__ == EventTypes.RE:
            pass
        elif self.startpos < cur_textlen:
            return Midletion(
                self.content,
                self.startpos,
                self.endpos,
                self.keyname,
                self.starttime,
                self.endtime,
                self.pause,
                cur_textlen,
            )
        else:
            return Deletion(
                self.content,
                self.startpos,
                self.endpos,
                self.keyname,
                self.starttime,
                self.endtime,
                self.pause,
                cur_textlen,
            )


class BDeletionKeyboardEvent(DeletionKeyboardEvent):
    def __init__(self, content, startpos, endpos, keyname, starttime, endtime, textlen):
        super().__init__(
            content, startpos, endpos, keyname, starttime, endtime, textlen
        )
        self.char_number_diff = CHAR_NUMBER_DIFF_BDELETION


class DDeletionKeyboardEvent(DeletionKeyboardEvent):
    def __init__(self, content, startpos, endpos, keyname, starttime, endtime, textlen):
        super().__init__(
            content, startpos, endpos, keyname, starttime, endtime, textlen
        )
        self.char_number_diff = CHAR_NUMBER_DIFF_DDELETION


class NavigationKeyboardEvent(KeyboardEvent):
    def __init__(self, content, startpos, endpos, keyname, starttime, endtime, textlen):
        super().__init__(
            content, startpos, endpos, keyname, starttime, endtime, textlen
        )

    def set_endpos(self):
        self.endpos = self.next_evnt.startpos

    def to_action(self):
        return Navigation(
            self.content,
            self.startpos,
            self.endpos,
            self.keyname,
            self.starttime,
            self.endtime,
            self.pause,
            self.textlen,
        )
