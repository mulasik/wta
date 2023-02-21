from .base import BaseEvent
from ..action import Replacement


class ReplacementEvent(BaseEvent):
    """
    A class to represent the replacement event.
    Replacement event is an event type stored in the idfx file.
    Replacement consists in marking a character sequence and replacing it with a character or empty sequence.

    Replacements are performed in two steps in the IDFX file:
        - first comes the key used for replacing (e.g. delete, backspace or character key)
        - then comes the replacement event.

    Example with delete:

    <event id="43" type="keyboard">
        <part type="wordlog">
            <position>140</position>
            <documentLength>162</documentLength>
            <replay>False</replay>
        </part>
        <part type="winlog">
            <startTime>24108355</startTime>
            <endTime>24108360</endTime>
            <key>VK_BACK</key>
            <value>&#x8;</value>
            <keyboardstate></keyboardstate>
        </part>
    </event>
    <event id="44" type="replacement">
        <part type="wordlog">
            <start>140</start>
            <end>161</end>
            <newtext></newtext>
        </part>
    </event>

    > The sequence slice [140:161] is marked and removed with the use of BACKSPACE at position 140.
    > The position of the last character in the marked sequence is 160.

    Example with character key:

    <event id="9" type="keyboard">
        <part type="wordlog">
            <position>25</position>
            <documentLength>3726</documentLength>
            <replay>False</replay>
        </part>
        <part type="winlog">
            <startTime>311419931</startTime>
            <endTime>311419936</endTime>
            <key>VK_I</key>
            <value>i</value>
            <keyboardstate></keyboardstate>
        </part>
    </event>
    <event id="10" type="replacement">
        <part type="wordlog">
            <start>25</start>
            <end>40</end>
            <newtext>i</newtext>
        </part>
    </event>
    """

    def __init__(self, content, startpos, endpos, rplcmt_endpos, rplcmt_textlen):
        super().__init__(content, startpos, endpos)
        self.rplcmt_endpos = rplcmt_endpos
        self.rplcmt_textlen = rplcmt_textlen

    def to_action(self):
        return Replacement(
            self.content,
            self.startpos,
            self.endpos,
            self.rplcmt_endpos,
            self.rplcmt_textlen,
        )
