from ...names import EventTypes
from ..action import Action, Append, Deletion, Insertion, Midletion, Navigation, Pasting
from .base import BaseEvent

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

    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        keyname: str,
        starttime: int,
        endtime: int,
        textlen: int,
        char_number_diff: int,
    ) -> None:
        super().__init__(content, startpos, endpos)
        self.keyname = keyname
        self.starttime = starttime
        self.endtime = endtime
        self.textlen = textlen
        self.pause: int | None = None
        self.char_number_diff = char_number_diff

    def set_pause(self) -> None:
        try:
            self.pause = (self.starttime - self.prev_evnt.starttime) / 1000
        except TypeError:
            self.pause = None
        except AttributeError:
            self.pause = None


class ProductionKeyboardEvent(KeyboardEvent):
    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        keyname: str,
        starttime: int,
        endtime: int,
        textlen: int,
    ) -> None:
        super().__init__(
            content,
            startpos,
            endpos,
            keyname,
            starttime,
            endtime,
            textlen,
            CHAR_NUMBER_DIFF_PRODUCTION,
        )

    def to_action(self) -> Action | None:
        cur_textlen = self.textlen - self.char_number_diff
        # if the next event is a replacement, the keyboard event is part of the replacement
        if type(self.next_evnt).__name__ == EventTypes.RE:
            return None
        # if more than 1 character has been produced at one go, the action is pasting
        if len(self.content) > 1:
            return Pasting(self.content, self.startpos, self.endpos, cur_textlen)
        # if position is smaller then text length
        if len(self.content) == 1 and self.startpos < cur_textlen:
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
    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        keyname: str,
        starttime: int,
        endtime: int,
        textlen: int,
        char_number_diff: int,
    ) -> None:
        super().__init__(
            content,
            startpos,
            endpos,
            keyname,
            starttime,
            endtime,
            textlen,
            char_number_diff,
        )

    def to_action(self) -> Action | None:
        cur_textlen = self.textlen - self.char_number_diff
        if type(self.next_evnt).__name__ == EventTypes.RE:
            return None
        if self.startpos < cur_textlen:
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
    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        keyname: str,
        starttime: int,
        endtime: int,
        textlen: int,
    ) -> None:
        super().__init__(
            content,
            startpos,
            endpos,
            keyname,
            starttime,
            endtime,
            textlen,
            CHAR_NUMBER_DIFF_BDELETION,
        )


class DDeletionKeyboardEvent(DeletionKeyboardEvent):
    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        keyname: str,
        starttime: int,
        endtime: int,
        textlen: int,
    ) -> None:
        super().__init__(
            content,
            startpos,
            endpos,
            keyname,
            starttime,
            endtime,
            textlen,
            CHAR_NUMBER_DIFF_DDELETION,
        )


class NavigationKeyboardEvent(KeyboardEvent):
    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        keyname: str,
        starttime: int,
        endtime: int,
        textlen: int,
    ) -> None:
        super().__init__(
            content, startpos, endpos, keyname, starttime, endtime, textlen, -1
        )

    def set_endpos(self) -> None:
        self.endpos = self.next_evnt.startpos

    def to_action(self) -> Action:
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
