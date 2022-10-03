from bs4 import BeautifulSoup
from tqdm import tqdm

from wta.pipeline.text_history.names import KeyNames
from .events.keyboard import (NavigationKeyboardEvent, ProductionKeyboardEvent,
                              BDeletionKeyboardEvent, DDeletionKeyboardEvent)
from .events.replacement import ReplacementEvent
from .events.insert import InsertEvent


class EventFactory:
    """
    A class for parsing the idfx file and transforming the keystroke events stored in the idfx format
    into Event objects used for generating actions, transforming sequences and text history in the next pipeline steps.

    Event types:
        * NavigationKeyboardEvent
        * BDeletionKeyboardEvent (deletion with backspace)
        * DDeletionKeyboardEvent (deletion with delete)
        * ProductionKeyboardEvent
        * ReplacementEvent
        * InsertEvent
    """

    def run(self, idfx) -> list:
        """
        Creates a list of Event objects.
        Args:
            idfx: an xml file containing the keystroke logs
        Returns:
            a list of Event objects
        """
        soup = BeautifulSoup(open(idfx), features="lxml")
        idfx_events = soup.find_all('event')
        idfx_events = tqdm(idfx_events, 'Processing keylogs')
        events = [self.create_event(event) for event in idfx_events]
        for i, event in enumerate(events):
            event.set_next_evnt(events[i+1] if i < len(events)-1 else None)
            event.set_prev_evnt(events[i-1] if i >= 1 else None)
            if event.prev_evnt:
                event.set_pause()
            if event.next_evnt:
                event.set_endpos()
        return events

    @staticmethod
    def create_event(event):
        """
        Collects event attributes and creates an object of type Event.
        Args:
            event: An object of type bs4.element.Tag containing event details as stored in the idfx file.
            Example:
                <event id="0" type="insert">
                    <part type="wordlog">
                        <position>31</position>
                        <before>Die Sprache ist ein Instrument.</before>
                        <after></after>
                    </part>
                </event>
        Returns:
            An Event object.

        EVENT ATTRIBUTES:
            * content: chars produced as result of keystroke
            * startpos: position of the cursor before keystroke
            * endpos: position of the cursor after keystroke
            * keyname: name of key in idfx
            * starttime: moment of pressing the key
            * endtime: moment of releasing the key
            * textlen: length of the text produced so far

        POSITIONS:
            Positions are "cells" where the character is placed.
            Startpos and endpos are retrieved from idfx file but for some event types, they must be modified to follow the same principle!
            The principle is as follows:
            |H|e|l|l|o| => |0|1|2|3|4| (append startpos == 0, endpos == 4)
            |e|l|l|o| => |1|2|3|4| (deletion startpos == 1, endpos == 4)
            |a|l|l|o| => |1|2|3|4| (append startpos == 1, endpos == 4)

        TEXT LENGTH:
            Text length provided in "documentLength" counts in the char just produced
            IT ALSO REFERS TO DELETION KEYS!
            So documentLength == position + 1.
            Example of char production:
                <event id="0" type="keyboard">
                    <part type="wordlog">
                        <position>0</position>
                        <documentLength>1</documentLength>
                        <replay>True</replay>
                    </part>
                    <part type="winlog">
                        <startTime>208726312</startTime>
                        <endTime>208726317</endTime>
                        <key>VK_W</key>
                        <value>W</value>
                        <keyboardstate></keyboardstate>
                    </part>
                </event>
            Example of char deletion (backspace pressed at pos 60 and documentLength == 61):
                <event id="60" type="keyboard">
                    <part type="wordlog">
                        <position>60</position>
                        <documentLength>61</documentLength>
                        <replay>True</replay>
                    </part>
                    <part type="winlog">
                        <startTime>208739505</startTime>
                        <endTime>208739510</endTime>
                        <key>VK_BACK</key>
                        <value>&#x8;</value>
                        <keyboardstate></keyboardstate>
                    </part>
                </event>
        """
        # CHARACTER PRODUCTION: characters are typed or deleted one by one OR writer navigates without editing
        if event['type'] == 'keyboard':
            parts = event.find_all('part')
            try:
                wordlog = parts[0]
                winlog = parts[1]
                content = winlog.value.get_text()
                startpos = int(wordlog.position.get_text())
                keyname = winlog.key.get_text()
                starttime = int(winlog.starttime.get_text())
                endtime = int(winlog.endtime.get_text())
                textlen = int(wordlog.documentlength.get_text())
                if keyname in KeyNames.NAVIGATION_KEYS:
                    endpos = None
                    evnt = NavigationKeyboardEvent(content, startpos, endpos, keyname, starttime, endtime, textlen)
                elif keyname in KeyNames.DELETION_KEYS:
                    if keyname == KeyNames.BACKSPACE:
                        startpos = startpos - 1
                        endpos = startpos
                        evnt = BDeletionKeyboardEvent(content, startpos, endpos, keyname, starttime, endtime, textlen)
                    elif keyname == KeyNames.DELETE:
                        endpos = startpos
                        evnt = DDeletionKeyboardEvent(content, startpos, endpos, keyname, starttime, endtime, textlen)
                else:
                    # first char is placed at startpos, so the char must be deduced from length:
                    endpos = startpos + (len(content) - 1)
                    evnt = ProductionKeyboardEvent(content, startpos, endpos, keyname, starttime, endtime, textlen)
            except IndexError:
                print('FAILURE: Keyboard event information not available in the IDFX file.')
        # SEQUENCE REPLACEMENT: a sequence is marked and replaced with a char or empty string
        elif event['type'] == 'replacement':
            try:
                content = event.part.newtext.get_text()  # character to replace marked sequence
                startpos = int(event.part.start.get_text())
                rplcmt_endpos = int(event.part.end.get_text())-1
                endpos = startpos + len(content)
                evnt = ReplacementEvent(content, startpos, endpos, rplcmt_endpos)
            except:
                print('FAILURE: Replacement event information not available in the IDFX file.')
        # SEQUENCE INSERTION: a text sequence is inserted
        elif event['type'] == 'insert':
            try:
                content = event.part.before.get_text()  # inserted text
                startpos = int(event.part.position.get_text()) - len(content)
                endpos = int(event.part.position.get_text()) - 1
                evnt = InsertEvent(content, startpos, endpos)
            except:
                print('FAILURE: Insert event information not available in the IDFX file.')
        else:
            print(f'ATTENTION: Encountered a new event type: {event["type"]}')
        return evnt

