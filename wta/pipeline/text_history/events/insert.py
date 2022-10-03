from .base import BaseEvent
from ..action import Pasting


class InsertEvent(BaseEvent):
    """
    A class to represent the insertion event.
    Insertion event is an event type stored in the idfx file.
    Insertion consists in pasting a character sequence.
    Exmaple from idfx file:
        <event id="0" type="insert">
            <part type="wordlog">
                <position>332</position>
                <before>
                    Die Sprache ist ein Instrument, welches uns hilft, das Umfeld sowie Handlungen zu benennen.
                    Dank diesem Mittel ist es uns möglich mit unserem sozialen Umfeld in Kontakt zu treten.
                    Darum bildet die Sprache ein erstes Sprungbrett für die Integration und die Zugehörigkeit zu einer Gesellschaft. Ich selbst bin bilingual aufgewachsen.
                </before>
                <after></after>
            </part>
        </event>

        <event id="0" type="insert">
            <part type="wordlog">
                <position>134</position>
                <before>
                    Liebe alle,
                    das ist ein Test, der versucht festzuhalten, ob Scriptlog das tut, was es soll.
                    Es wäre ungünstig, wenn es das nicht täte.
                </before>
                <after></after>
            </part>
        </event>
    """

    def __init__(self, content, startpos, endpos):
        super().__init__(content, startpos, endpos)
        # print(f'InsertEvent: {self.__dict__["content"]} {self.__dict__["startpos"]} {self.__dict__["endpos"]}')

    def to_action(self):
        return Pasting(self.content, self.startpos, self.endpos)

