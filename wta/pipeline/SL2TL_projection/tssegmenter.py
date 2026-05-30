import re
from typing import TypedDict

from wta.pipeline.BL2TL_projection.burst import Burst
from wta.pipeline.BL2TL_projection.burst_factory import BurstFactory
from wta.pipeline.names import SegmentTypes, SScope, TSLabels, TUState, TUTypes
from wta.pipeline.preprocessing.action import Action, KeyboardAction
from wta.pipeline.SL2TL_projection.segment import Segment
from wta.pipeline.SL2TL_projection.textunit import TextunitBuilder
from wta.pipeline.transformation_layer.ts import TSBuilder


class TSSegmenterDict(TypedDict):
    tpsf_id: int
    tpsf_text: str
    transformation_text: str
    transformation_scope: str
    ts_label: str
    duration: float | None
    length: int
    preceding_pause: int
    bursts: list[Burst]
    sentence_segments: list[Segment]


class TSSegmenter:
    """
    In case of production operation (app or ins) the following scenarios are possible:
    SEN
    * a SEN is created --> state NEW
    IN_SEN
    * an end of a SEN is created --> state MOD
    * a new begginging of a SEN or SEC is created --> state MOD
    * a new middle a SEN or SEC in created --> state MOD
    NO_SEN
    * just empty space added to the text
    CROSS_SEN or MULTI_SEN
    * (MOD SEN|SEC)? --- NEW SEN+ --- ((MOD SEN|SEC) | NEW SEC)?
    Attention: CROSS_SEN and MULTI_SEN never result in modification of a SEN / SEC middle. This cannot occur.
    """
    def __init__(
            self,
            tpsf_id: int,
            tpsf_text: str,
            ts: TSBuilder,
            sscope: str,
            textunits: list[TextunitBuilder],
            impacted_tus_prev: list[TextunitBuilder],
            prev_tpsf_text: str|None
        ) -> None:
        self.tpsf_id = tpsf_id
        self.tpsf_text = tpsf_text
        self.ts = ts
        self.sscope = sscope
        self.textunits = textunits
        self.impacted_tus_prev = impacted_tus_prev
        self.prev_tpsf_text = prev_tpsf_text
        self.impacted_tus = [
            tu for tu in textunits
            if tu.state in [TUState.MOD, TUState.NEW, TUState.MER, TUState.SPLIT]
        ]
        self.spsfs = [
            tu for tu in textunits
            if tu.type in (TUTypes.SEN, TUTypes.SEC)
        ]
        self.impacted_spsfs_prev = [
            ptu for ptu in impacted_tus_prev
            if ptu.type in (TUTypes.SEN, TUTypes.SEC)
        ]
        self.modified_spsfs = [spsf for spsf in self.spsfs if spsf.state in [TUState.MOD, TUState.MER, TUState.SPLIT]]
        self.new_spsfs = [spsf for spsf in self.spsfs if spsf.state == TUState.NEW]
        self.impacted_spsfs = [*self.modified_spsfs, *self.new_spsfs]

    def run(self) -> list[Segment]:
        # print(f"\nRunning TS segmenter for TPSF {self.tpsf_id} with TS label {self.ts.label} and TS text |{self.ts.text}|.")
        if self.ts.text == "":
            print(f"INFO: The TS text for operation {self.ts.label.upper()} is empty, hence no segments have been generated.")
            segments = []
        else:
            segments = self._generate_segments(self.impacted_tus, self.ts.startpos, self.ts.endpos, self.ts.following_pause, self.ts.pauses, self.ts.actions, self.tpsf_text)
        spsf_segments = [s for s in segments if s.segment_type.strip() not in [SegmentTypes.SIN, SegmentTypes.PIN]]
        # generate warning if inconsistency detected
        # between the number of impacted TUs and number of segments
        if (
            # inconsistency in opt1 (whole SPSF produced)
            (self.sscope in [SScope.SEN, SScope.SEC] and len(spsf_segments) != 1)
            or
            # inconsistency in opt2 (in-sentence production)
            (self.sscope == SScope.IN_SEN and len(spsf_segments) != 1)
            or
            # inconsistency in opt3 (if the transformation does not refer to an SPSF)
            (self.sscope == SScope.NO_SEN and len(spsf_segments) > 0)
            or
            # inconsistency in opt4 (a cross-sentence or multi-sentence modification / production)
            (self.sscope in [SScope.CROSS_SEN, SScope.MULTI_SEN] and len(spsf_segments) != len(self.impacted_spsfs))
        ):
            print(self._generate_ts_extraction_warning(self.impacted_tus, None, segments))
        if self.sscope in [SScope.CROSS_SEN, SScope.MULTI_SEN] and len(segments) == 1 and not re.fullmatch(r"(\.|\?|\!)", segments[0].text):
            print(self._generate_definition_incompatibility_warning(segments))
        return segments

    def _generate_ts_extraction_warning(
            self,
            impacted_tus: list[TextunitBuilder] | None,
            impacted_tus_prev: list[TextunitBuilder] | None,
            segments: list[Segment]
        ) -> str:
        msg_impacted = f"""
There are {len(impacted_tus)} impacted TUs:
{[(s.text, s.state) for s in impacted_tus]}
""" if impacted_tus == [] or impacted_tus is not None else ""

        msg_prev_impacted = f"""
There are {len(impacted_tus_prev)} impacted TUs in previous TPSF:
{[(s.text, s.state) for s in impacted_tus_prev]}
""" if impacted_tus_prev == [] or impacted_tus_prev is not None else ""

        return f"""
\033[31mWARNING for TPSF {self.tpsf_id}:
Could not extract segments of TS of type {self.ts.label} for scope *{self.sscope}*.
The content of the TS:
|{self.ts.text}| ({self.ts.startpos}-{self.ts.endpos}).
The segments: {[str(s) for s in segments]}
{msg_impacted}{msg_prev_impacted}
Was not able to match the TS with the impacted SPSFs.\033[0m
"""

    def _generate_definition_incompatibility_warning(
            self,
            segments: list[Segment] | None = None
    ) -> str:
        segment_list = f"Segments: {[seg.text for seg in segments]}" if segments else ""
        return f"""
\033[31mWARNING for TPSF {self.tpsf_id}: Definition incompatibility!
{segment_list}
The first modified SPSF does not end with end punctuation mark or newline.
According to the definition, it should be merged with the following SPSF.\033[0m
"""

    def _extract_segment_type(self, tu: TextunitBuilder, startpos: int, endpos: int) -> str:
        if tu.type == TUTypes.SIN:
            segment_type = SegmentTypes.SIN
        elif tu.type == TUTypes.PIN:
            segment_type = SegmentTypes.PIN
        elif startpos == tu.startpos and endpos == tu.endpos:
            if tu.type == TUTypes.SEC:
                segment_type = SegmentTypes.SEC
            if tu.type == TUTypes.SEN:
                segment_type = SegmentTypes.SEN
        elif startpos == tu.startpos and endpos is not None and tu.endpos is not None and endpos != tu.endpos and tu.text[endpos:tu.endpos+1].strip() != "":
            segment_type = SegmentTypes.SEN_BEG
        elif startpos == tu.startpos and endpos is not None and tu.endpos is not None and endpos != tu.endpos and tu.text[endpos:tu.endpos+1].strip() == "":
            segment_type = SegmentTypes.SEC if tu.type == TUTypes.SEC else SegmentTypes.SEN
        elif startpos != tu.startpos and endpos == tu.endpos and tu.type == TUTypes.SEN:
            segment_type = SegmentTypes.SEN_END
        else:
            segment_type = SegmentTypes.SEN_MID
        return segment_type

    def _generate_segments(
            self,
            tus: list[TextunitBuilder],
            ts_startpos: int,
            ts_endpos: int|None,
            ts_following_pause: float|None,
            pauses: list[float],
            actions: list[Action],
            tpsf_text: str|None,
        ) -> list[Segment]:

        segments: list[Segment] = []
        startpos = ts_startpos
        for i, tu in enumerate(tus):
            if tu.endpos is not None and ts_endpos is not None:
                endpos = tu.endpos if i != len(tus)-1 else ts_endpos
                segment_text = None if tpsf_text is None else tpsf_text[startpos:endpos+1]
                if segment_text is not None and segment_text != "":
                    segment_type = self._extract_segment_type(tu, startpos, endpos)
                    relative_startpos = startpos - ts_startpos
                    relative_endpos = endpos - ts_startpos
                    if len(pauses) > 0:
                        relevant_pauses = pauses[relative_startpos:relative_endpos+1]
                        preceding_pause = relevant_pauses[0]
                        following_pause = pauses[relative_endpos+1:relative_endpos+2][0] if len(pauses) > relative_endpos+1 else ts_following_pause
                        if len(actions) > relative_startpos:
                            starttime = actions[relative_startpos].starttime if isinstance(actions[relative_startpos], KeyboardAction) else None
                        else:
                            starttime = None
                        if len(actions) >= relative_endpos+1:
                            endtime = actions[relative_endpos].starttime if isinstance(actions[relative_endpos], KeyboardAction) else None
                        else:
                            endtime = None

                        segment_bursts = BurstFactory().run(segment_text, relevant_pauses, following_pause, self.tpsf_id, self.ts.label)
                    else:
                        preceding_pause, following_pause, starttime, endtime, segment_bursts = None, None, None, None, []
                    segment = Segment(
                        segment_text,
                        segment_type,
                        startpos,
                        endpos,
                        relative_startpos,
                        relative_endpos,
                        preceding_pause,
                        following_pause,
                        starttime,
                        endtime,
                        # segment_bursts
                    )
                    segments.append(segment)
                    if self.ts.label not in [TSLabels.DEL, TSLabels.MID]:
                        tu.assign_segment(segment)
                    else:
                        tu_text_after_deletion = None if tpsf_text is None else tpsf_text[tu.startpos:startpos] + tpsf_text[endpos+1:tu.endpos+1]
                        for tunit in self.textunits:
                            if tunit.text == tu_text_after_deletion:
                                tunit.assign_segment(segment)
                else:
                    print(f"INFO: The segment text for operation {self.ts.label.upper()} is empty, hence has not been added to the segment list.")
                startpos = tu.endpos + 1

        # print(f"\nTS SEGMENT DETAILS FOR {len(self.impacted_tus)} IMPACTED TU(s):")
        # for ind, tsseg in enumerate(segments):
        #     print()
        #     print(f"TU / SEG {ind}: {tsseg!s}")

        return segments


class DelTSSegmenter (TSSegmenter):
    """
    In case of deletion operation (del or mid) the following scenarios are possible:
    SEN
    * a SEN or SEC is deleted --> state DEL
    IN_SEN
    * an end of a SEN is deleted --> state MOD
    * a begginging of a SEN or SEC is deleted --> state MOD
    * a middle a SEN or SEC in deleted --> state MOD
    NO_SEN
    * just empty space deleted
    CROSS_SEN or MULTI_SEN
    * (DEL SENend|SECend|SEC)? --- DEL SEN+ --- (DEL SENbeg|SECbeg|SEC)?
    Attention: CROSS_SEN and MULTI_SEN never result in deletion of a SEN / SEC middle. This cannot occur.
    """
    def __init__(
            self,
            tpsf_id: int,
            tpsf_text: str,
            ts: TSBuilder,
            sscope: str,
            textunits: list[TextunitBuilder],
            impacted_tus_prev: list[TextunitBuilder],
            prev_tpsf_text: str|None
        ) -> None:

        super().__init__(tpsf_id, tpsf_text, ts, sscope, textunits, impacted_tus_prev, prev_tpsf_text)
        self.deleted_spsfs = [spsf for spsf in self.impacted_spsfs_prev if spsf.state == TUState.DEL]
        self.deleted_tus = [tu for tu in self.textunits if tu.state == TUState.DEL]

    def run(self) -> list[Segment]:
        segments = self._generate_segments(self.impacted_tus_prev, self.ts.startpos, self.ts.endpos, self.ts.following_pause, self.ts.pauses, self.ts.actions, self.prev_tpsf_text)
        spsf_segments = [s for s in segments if s.segment_type.strip() not in [SegmentTypes.SIN, SegmentTypes.PIN]]
        # generate warning if inconsistency detected
        # between the number of impacted TUs and number of segments
        if (
            # inconsistency in opt1 (whole SPSF produced)
            (self.sscope in [SScope.SEN, SScope.SEC] and len(spsf_segments) != 1)
            or
            # inconsistency in opt2 (in-sentence production)
            (self.sscope == SScope.IN_SEN and len(spsf_segments) != 1)
            or
            # inconsistency in opt3 (if the transformation does not refer to an SPSF)
            (self.sscope == SScope.NO_SEN and len(spsf_segments) > 0)
            or
            # inconsistency in opt4 (a cross-sentence or multi-sentence modification / production)
            (self.sscope in [SScope.CROSS_SEN, SScope.MULTI_SEN] and len(spsf_segments) != len(self.impacted_spsfs_prev))
        ):
            print(self._generate_ts_extraction_warning(self.impacted_tus, None, segments))
        if self.sscope in [SScope.CROSS_SEN, SScope.MULTI_SEN] and len(segments) == 1 and not re.fullmatch(r"(\.|\?|\!)", segments[0].text):
            print(self._generate_definition_incompatibility_warning(segments))
        return segments


class ReplTSSegmenter (TSSegmenter):
    """
    In case of replacement operation the following scenarios are possible:
    SEN
    * a SEN or SEC is created --> NEW SEN|SEC
    IN_SEN
    * an end of a SEN is created --> state MOD
    * a begginging of a SEN or SEC is created --> state MOD
    * a middle a SEN or SEC in created --> state MOD
    NO_SEN
    * just empty space created
    CROSS_SEN or MULTI_SEN
    * (MOD SEN|SEC)? --- NEW SEN+ --- (MOD SEN|SEC)?
    Attention: CROSS_SEN and MULTI_SEN never result in creation of a SEN / SEC middle. This cannot occur.
    """
    def __init__(
            self,
            tpsf_id: int,
            tpsf_text: str,
            ts: TSBuilder,
            sscope: str,
            textunits: list[TextunitBuilder],
            impacted_tus_prev: list[TextunitBuilder],
            prev_tpsf_text: str|None
        ) -> None:
        super().__init__(tpsf_id, tpsf_text, ts, sscope, textunits, impacted_tus_prev, prev_tpsf_text)
        self.deleted_spsfs = [spsf for spsf in self.impacted_spsfs_prev if spsf.state == TUState.DEL]
        self.deleted_tus = [tu for tu in self.textunits if tu.state == TUState.DEL]

    def run(self) -> list[Segment]:
        if self.ts.text == "":
            print(f"INFO: The TS text for operation {self.ts.label.upper()} is empty, hence no segments have been generated.")
            segments = []
        else:
            segments = self._generate_segments(self.impacted_tus, self.ts.startpos, self.ts.endpos, self.ts.following_pause, self.ts.pauses, self.ts.actions, self.tpsf_text)
        spsf_segments = [s for s in segments if s.segment_type.strip() not in [SegmentTypes.SIN, SegmentTypes.PIN]]
        # generate warning if inconsistency detected
        # between the number of impacted TUs and number of segments
        if (
            # inconsistency in opt1 (whole SPSF produced),
            # in case of replacement the segments list if often empty, as the replacing sequence is empty (e.g. when marking text and entering backspace)
            # in that case len(spsf_segments) == 0
            (self.sscope in [SScope.SEN, SScope.SEC] and len(spsf_segments) > 1)
            or
            # inconsistency in opt2 (in-sentence production)
            # in case of replacement the segments list if often empty, as the replacing sequence is empty (e.g. when marking text and entering backspace)
            # in that case len(spsf_segments) == 0
            (self.sscope == SScope.IN_SEN and len(spsf_segments) > 1)
            or
            # inconsistency in opt3 (if the transformation does not refer to an SPSF)
            (self.sscope == SScope.NO_SEN and len(spsf_segments) > 0)
            or
            # inconsistency in opt4 (a cross-sentence or multi-sentence modification / production)
            (self.sscope in [SScope.CROSS_SEN, SScope.MULTI_SEN] and len(spsf_segments) > 0 and len(spsf_segments) != len(self.impacted_spsfs))
        ):
            print(self._generate_ts_extraction_warning(self.impacted_tus, None, segments))
        if self.sscope in [SScope.CROSS_SEN, SScope.MULTI_SEN] and len(segments) == 1 and not re.fullmatch(r"(\.|\?|\!)", segments[0].text):
            print(self._generate_definition_incompatibility_warning(segments))
        return segments


    def segment_replaced_text(self) -> list[Segment]:
        startpos = self.ts.startpos
        endpos = None if self.ts.rplcmt_textlen is None else self.ts.startpos+self.ts.rplcmt_textlen-1
        segments = self._generate_segments(self.impacted_tus_prev, startpos, endpos, self.ts.following_pause, self.ts.pauses, self.ts.actions, self.prev_tpsf_text)
        spsf_segments = [s for s in segments if s.segment_type.strip() not in [SegmentTypes.SIN, SegmentTypes.PIN]]
        # generate warning if inconsistency detected
        # between the number of impacted TUs and number of segments
        if (
            # inconsistency in opt1 (whole SPSF produced)
            (self.sscope in [SScope.SEN, SScope.SEC] and len(spsf_segments) != 1)
            or
            # inconsistency in opt2 (in-sentence production)
            (self.sscope == SScope.IN_SEN and len(spsf_segments) != 1)
            or
            # inconsistency in opt3 (if the transformation does not refer to an SPSF)
            (self.sscope == SScope.NO_SEN and len(spsf_segments) > 1)
            or
            # inconsistency in opt4 (a cross-sentence or multi-sentence modification / production)
            (self.sscope in [SScope.CROSS_SEN, SScope.MULTI_SEN] and len(spsf_segments) != len(self.impacted_spsfs_prev))
        ):
            print(self._generate_ts_extraction_warning(self.impacted_tus, None, segments))
        if self.sscope in [SScope.CROSS_SEN, SScope.MULTI_SEN] and len(segments) == 1 and not re.fullmatch(r"(\.|\?|\!)", segments[0].text):
            print(self._generate_definition_incompatibility_warning(segments))
        return segments
