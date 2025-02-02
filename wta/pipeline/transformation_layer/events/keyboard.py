from wta.settings import Settings

from ...names import EventTypes
from ..action import Action, Append, Deletion, Insertion, Midletion, Navigation, Pasting
from .base import BaseEvent

CHAR_NUMBER_DIFF_MAPPING = {
    "scriptlog_idfx": {
        "production": 1,
        "ddeletion": 1,
        "bdeletion": 2
        # Document length in the idfx file == position + 1.
        # In case of backspace deletion the startpos == startpos - 1 because this is where the char actually gets deleted.
        # So the total diff is 2 between the position of the deleted char and the document length provided in idfx.
    },
    "inputlog_idfx": {"production": 1, "ddeletion": 1, "bdeletion": 2},
    "protext_csv": {"production": 0, "ddeletion": 0, "bdeletion": 0},
}


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
        starttime: float,
        endtime: float,
        textlen: int,
        settings: Settings,
        char_number_diff: int,
    ) -> None:
        super().__init__(content, startpos, endpos)
        self.keyname = keyname
        self.starttime = starttime
        self.endtime = endtime
        self.preceding_pause = None
        self.textlen = textlen
        self.settings = settings
        self.char_number_diff = char_number_diff

    def set_preceding_pause(self) -> None:
        if isinstance(self.prev_evnt, KeyboardEvent):
            try:
                self.preceding_pause = round(self.starttime - self.prev_evnt.starttime, 4)
            except TypeError:
                self.preceding_pause = None
        else:
            self.preceding_pause = None


class ProductionKeyboardEvent(KeyboardEvent):
    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        keyname: str,
        starttime: float,
        endtime: float,
        textlen: int,
        settings: Settings,
    ) -> None:
        super().__init__(
            content,
            startpos,
            endpos,
            keyname,
            starttime,
            endtime,
            textlen,
            settings,
            # CHAR_NUMBER_DIFF_PRODUCTION,
            CHAR_NUMBER_DIFF_MAPPING[settings.config["ksl_source_format"]][
                "production"
            ],
        )

    def to_action(self) -> Action | None:
        cur_textlen = self.textlen - self.char_number_diff
        # if the next event is a replacement, the keyboard event is part of the replacement
        if type(self.next_evnt).__name__ == EventTypes.RE:
            return None
        # if more than 1 character has been produced at one go, the action is pasting
        if len(self.content) > 1:
            return Pasting(self.content, self.startpos, self.endpos)
        # if position is smaller then text length
        if len(self.content) == 1 and self.startpos < cur_textlen:
            return Insertion(
                self.content,
                self.startpos,
                self.endpos,
                self.keyname,
                self.starttime,
                self.endtime,
                self.preceding_pause,
                cur_textlen,
            )
        return Append(
            self.content,
            self.startpos,
            self.endpos,
            self.keyname,
            self.starttime,
            self.endtime,
            self.preceding_pause,
            cur_textlen,
        )


class DeletionKeyboardEvent(KeyboardEvent):
    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        keyname: str,
        starttime: float,
        endtime: float,
        textlen: int,
        settings: Settings,
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
            settings,
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
                self.preceding_pause,
                cur_textlen,
            )
        return Deletion(
            self.content,
            self.startpos,
            self.endpos,
            self.keyname,
            self.starttime,
            self.endtime,
            self.preceding_pause,
            cur_textlen,
        )


class BDeletionKeyboardEvent(DeletionKeyboardEvent):
    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        keyname: str,
        starttime: float,
        endtime: float,
        textlen: int,
        settings: Settings,
    ) -> None:
        super().__init__(
            content,
            startpos,
            endpos,
            keyname,
            starttime,
            endtime,
            textlen,
            settings,
            CHAR_NUMBER_DIFF_MAPPING[settings.config["ksl_source_format"]]["bdeletion"],
        )


class DDeletionKeyboardEvent(DeletionKeyboardEvent):
    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        keyname: str,
        starttime: float,
        endtime: float,
        textlen: int,
        settings: Settings,
    ) -> None:
        super().__init__(
            content,
            startpos,
            endpos,
            keyname,
            starttime,
            endtime,
            textlen,
            settings,
            CHAR_NUMBER_DIFF_MAPPING[settings.config["ksl_source_format"]]["ddeletion"],
        )


class NavigationKeyboardEvent(KeyboardEvent):
    def __init__(
        self,
        content: str,
        startpos: int,
        endpos: int | None,
        keyname: str,
        starttime: float,
        endtime: float,
        textlen: int,
        settings: Settings,
    ) -> None:
        super().__init__(
            content,
            startpos,
            endpos,
            keyname,
            starttime,
            endtime,
            textlen,
            settings,
            -1,
        )

    # def set_endpos(self) -> None:
    #     if self.next_evnt is None:
    #         msg = "Next event is not set. Therefore no endpos can be set."
    #         raise RuntimeError(msg)
    #     self.endpos = self.next_evnt.startpos

    def to_action(self) -> Action:
        return Navigation(
            self.content,
            self.startpos,
            self.endpos,
            self.keyname,
            self.starttime,
            self.endtime,
            self.preceding_pause,
            self.textlen,
        )
