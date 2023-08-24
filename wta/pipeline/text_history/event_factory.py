import csv
from collections.abc import Iterable
from pathlib import Path

from bs4 import BeautifulSoup, Tag
from tqdm import tqdm

from wta.settings import Settings

from ..names import KeyNames
from .events.base import BaseEvent
from .events.insert import InsertEvent
from .events.keyboard import (
    BDeletionKeyboardEvent,
    DDeletionKeyboardEvent,
    NavigationKeyboardEvent,
    ProductionKeyboardEvent,
)
from .events.replacement import ReplacementEvent


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

    def run(self, ksl_file: Path, settings: Settings) -> list[BaseEvent]:
        """
        Creates a list of Event objects.
        Args:
            idfx: xml file containing the keystroke logs
        Returns:
            list of Event objects
        """
        if settings.config["ksl_source_format"] in ["scriptlog_idfx", "inputlog_idfx"]:
            events = self.extract_events_from_scriptlog_idfx(ksl_file, settings)
        elif settings.config["ksl_source_format"] == "protext_csv":
            events = self.extract_events_from_protext_csv(ksl_file, settings)
        for i, event in enumerate(events):
            event.set_next_evnt(events[i + 1] if i < len(events) - 1 else None)
            event.set_prev_evnt(events[i - 1] if i >= 1 else None)
            if event.prev_evnt:
                event.set_pause()
            if event.next_evnt:
                event.set_endpos()
        return events

    def extract_events_from_scriptlog_idfx(
        self, idfx: Path, settings: Settings
    ) -> list[BaseEvent]:
        with idfx.open() as fp:
            soup = BeautifulSoup(fp, features="lxml")
            idfx_events: Iterable[Tag] = soup.find_all("event")
        idfx_events = tqdm(idfx_events, "Processing keylogs")
        events = [
            event_obj
            for event_obj in (
                self.create_event_from_scriptlog_idfx(event, settings)
                for event in idfx_events
            )
            if event_obj is not None
        ]
        return events

    def clean_keystroke_logs(
        self, keystroke_logs: list[dict[str, int | str]]
    ) -> list[dict[str, int | str]]:
        # print("=========keystroke_logs==========")
        # for ksl in keystroke_logs:
        #     print(ksl)
        cleaned_keystroke_logs = []
        doc_len_correction = 0
        for ks_log in keystroke_logs:
            if ks_log["event"] == "^" and ks_log["op"] != "0":
                doc_len_correction -= 1
                # print(f"*** Need to reduce the doc length by {doc_len_correction}")
            else:
                clean_ks_log: dict[str, int | str] = {}
                clean_ks_log["st_time"] = int(ks_log["st_time"])
                clean_ks_log["end_time"] = int(ks_log["end_time"])
                clean_ks_log["pause"] = (
                    -1 if not ks_log["pause"] else int(ks_log["pause"])
                )
                clean_ks_log["event"] = str(ks_log["event"])
                clean_ks_log["pos"] = int(ks_log["pos"])
                # print("Previous doc len:", ks_log["doc_len"], int(ks_log["pos"]))
                clean_ks_log["doc_len"] = int(ks_log["doc_len"]) + doc_len_correction
                # print("Corrected doc len:", clean_ks_log["doc_len"], int(ks_log["pos"]))
                clean_ks_log["op"] = int(ks_log["op"])
                clean_ks_log["type_op"] = str(ks_log["type_op"])
                cleaned_keystroke_logs.append(clean_ks_log)
        # print("==========cleaned_keystroke_logs=========")
        # for ksl in cleaned_keystroke_logs:
        #     print(ksl)
        return cleaned_keystroke_logs

    def extract_events_from_protext_csv(
        self, csv_file: Path, settings: Settings
    ) -> list[BaseEvent]:
        file = csv_file.open()
        csv_reader = csv.DictReader(
            file,
            fieldnames=[
                "ID",
                "session",
                "writer",
                "n_event",
                "st_time",
                "end_time",
                "pause",
                "event",
                "pos",
                "doc_len",
                "op",
                "type_op",
                "charID",
            ],
        )
        cleaned_keystroke_logs = self.clean_keystroke_logs(list(csv_reader)[1:])
        keystroke_logs = tqdm(cleaned_keystroke_logs, "Processing keylogs")
        events = []
        for ks_log in keystroke_logs:
            if ks_log["type_op"] != "correction":
                event = self.create_event_from_protext_ks_log(ks_log, settings)
                if event is not None:
                    events.append(event)
        return events

    @staticmethod
    def create_event_from_scriptlog_idfx(
        event: Tag, settings: Settings
    ) -> BaseEvent | None:
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
        if event["type"] == "keyboard":
            parts = event.find_all("part")
            try:
                wordlog = parts[0]
                winlog = parts[1]
                content = winlog.value.get_text()
                startpos = int(wordlog.position.get_text())
                keyname = winlog.key.get_text()
                starttime = int(winlog.starttime.get_text())
                endtime = int(winlog.endtime.get_text())
                textlen = int(wordlog.documentlength.get_text())
                if keyname in KeyNames.SHIFT_KEYS:
                    return None
                if keyname in KeyNames.NAVIGATION_KEYS:
                    endpos = None
                    return NavigationKeyboardEvent(
                        content,
                        startpos,
                        endpos,
                        keyname,
                        starttime,
                        endtime,
                        textlen,
                        settings,
                    )
                if keyname in KeyNames.DELETION_KEYS:
                    if keyname == KeyNames.BACKSPACE:
                        startpos = (
                            startpos - 1 if startpos > 0 else 0
                        )  # if backspace is pressed at the beginning of the document
                        endpos = startpos
                        return BDeletionKeyboardEvent(
                            content,
                            startpos,
                            endpos,
                            keyname,
                            starttime,
                            endtime,
                            textlen,
                            settings,
                        )
                    if keyname == KeyNames.DELETE:
                        endpos = startpos
                        return DDeletionKeyboardEvent(
                            content,
                            startpos,
                            endpos,
                            keyname,
                            starttime,
                            endtime,
                            textlen,
                            settings,
                        )
                else:
                    # first char is placed at startpos, so the char must be deduced from length:
                    endpos = startpos + (len(content) - 1)
                    return ProductionKeyboardEvent(
                        content,
                        startpos,
                        endpos,
                        keyname,
                        starttime,
                        endtime,
                        textlen,
                        settings,
                    )
            except IndexError:
                print(
                    "FAILURE: Keyboard event information not available in the IDFX file."
                )
        # SEQUENCE REPLACEMENT: a sequence is marked and replaced with a char or empty string
        elif event["type"] == "replacement":
            try:
                content = (
                    event.part.newtext.get_text()
                )  # character to replace marked sequence
                orig_startpos = int(event.part.start.get_text())
                orig_endpos = int(event.part.end.get_text())
                endpos = orig_startpos + len(content)
                rplcmt_textlen = orig_endpos - orig_startpos
                rplcmt_endpos = orig_endpos - 1
                return ReplacementEvent(
                    content, orig_startpos, endpos, rplcmt_endpos, rplcmt_textlen
                )
            except:
                print(
                    "FAILURE: Replacement event information not available in the IDFX file."
                )
        # SEQUENCE INSERTION: a text sequence is inserted
        elif event["type"] == "insert":
            try:
                content = event.part.before.get_text()  # inserted text
                startpos = int(event.part.position.get_text()) - len(content)
                endpos = int(event.part.position.get_text()) - 1
                return InsertEvent(content, startpos, endpos)
            except:
                print(
                    "FAILURE: Insert event information not available in the IDFX file."
                )
        elif event["type"] in ["mouse", "focus", "selection", "statistics"]:
            pass
        else:
            print(f'ATTENTION: Encountered a new event type: {event["type"]}')
        return None

    @staticmethod
    def create_event_from_protext_ks_log(
        event: dict[str, int | str], settings: Settings
    ) -> BaseEvent | None:
        # TODO extend the mappings!
        symbol_content_mapping = {
            "␣": " ",
            "⌫": "&#x8;",
            "↲": "\n",
            "⌦": "",
            "⇆": "\t",
        }
        content_vk_mapping = {
            " ": "VK_SPACE",
            "&#x8;": "VK_BACK",
            "\n": "VK_RETURN",
            "": "VK_DELETE",
            "\t": "VK_TAB",
        }
        operation = int(event["op"])
        event_type = str(event["type_op"])
        event_content = str(event["event"])
        content = str(
            event_content
            if event_content not in symbol_content_mapping
            else symbol_content_mapping[event_content]
        )
        startpos = int(event["pos"])
        keyname = str(
            f"VK_{content.upper()}"
            if content not in content_vk_mapping
            else content_vk_mapping[content]
        )
        starttime = int(event["st_time"])
        endtime = int(event["end_time"])
        textlen = int(event["doc_len"])
        # CHARACTER PRODUCTION: characters are typed or deleted one by one OR writer navigates without editing
        if event_type in ["keyboard", "insert/replace"]:
            try:
                if operation == -1:
                    if keyname == KeyNames.BACKSPACE:
                        startpos = (
                            startpos - 1 if startpos > 0 else 0
                        )  # if backspace is pressed at the beginning of the document
                        endpos = startpos
                        return BDeletionKeyboardEvent(
                            content,
                            startpos,
                            endpos,
                            keyname,
                            starttime,
                            endtime,
                            textlen,
                            settings,
                        )
                    if keyname == KeyNames.DELETE:
                        endpos = startpos
                        return DDeletionKeyboardEvent(
                            content,
                            startpos,
                            endpos,
                            keyname,
                            starttime,
                            endtime,
                            textlen,
                            settings,
                        )
                elif operation == 1:
                    # first char is placed at startpos, so the char must be deduced from length:
                    endpos = startpos + (len(content) - 1)
                    return ProductionKeyboardEvent(
                        content,
                        startpos,
                        endpos,
                        keyname,
                        starttime,
                        endtime,
                        textlen,
                        settings,
                    )
            except IndexError:
                print(
                    f"FAILURE: Event information not available in the IDFX file (event {event_type})."
                )
        else:
            print(f"ATTENTION: Encountered a new event type: {event_type}")
        return None
