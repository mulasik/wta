import json
import re
from typing import TypedDict

from wta.pipeline.names import PointOfInscription, SenSegmentTypes, TextTransScope
from wta.pipeline.transformation_layer.text_transformation_segment import (
    TextTransformationSegment,
    TextTransformationSegmentDict,
)
from wta.pipeline.transformation_layer.text_unit import TextUnit
from wta.pipeline.transformation_layer.ts import TransformingSequence
from wta.pipeline.transformation_layer.ts_burst import TSBurst


class TextTransformationDict(TypedDict):
    tpsf_id: int
    tpsf_text: str
    transformation_text: str
    transformation_scope: str
    ts_label: str
    duration: float | None
    length: int
    preceding_pause: int
    bursts: list[TSBurst]
    sentence_segments: list[TextTransformationSegmentDict]


class TextTransformation:

    def __init__(
            self,
            tpsf_id: int,
            tpsf_text: str,
            scope: str,
            impacted_spsfs: list[TextUnit],
            ts: TransformingSequence,
        ) -> None:
        self.tpsf_id = tpsf_id
        self.tpsf_text = tpsf_text
        self.ts = ts
        self.scope = scope
        self.impacted_spsfs = impacted_spsfs
        self.sentence_segments: list[TextTransformationSegment] = []

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)

    def to_dict(self) -> TextTransformationDict:
        return {
            "tpsf_id": self.tpsf_id,
            "tpsf_text": self.tpsf_text,
            "transformation_text": self.ts.text,
            "transformation_scope": self.scope,
            "ts_label": self.ts.label,
            "duration": self.ts.duration,
            "length": len(self.ts.text),
            "preceding_pause": self.ts.preceding_pause,
            "bursts": [ss.to_dict() for ss in self.ts.bursts],
            "sentence_segments": [seg.to_dict() for seg in self.sentence_segments]
        }

    def to_text(self) -> str:
        str = f"""
TPSF {self.tpsf_id}
{self.tpsf_text}
*TS label & transformation scope*
{self.ts.label} - {self.scope}
*Time*
Preceding pause {self.ts.preceding_pause,}
Duration: {self.ts.duration}
Writing speed per minute: {self.ts.writing_speed_per_min}
Avg pause duration: {self.ts.avg_pause_duration}
*Sentence segments*
"""
        for seg in self.sentence_segments:
            str += f"{seg.segment_type}: {seg.text} ({seg.length})\n"
        return str

class TextProdTransformation (TextTransformation):

    def __init__(
            self,
            tpsf_id: int,
            tpsf_text: str,
            scope: str,
            impacted_spsfs: list[TextUnit],
            ts: TransformingSequence,
            prev_tpsf_text: str
        ) -> None:
        super().__init__(tpsf_id, tpsf_text, scope, impacted_spsfs, ts)
        print(f"Calculating point of inscription for production: start at {ts.startpos}, prev_tpsf_textlen: {len(prev_tpsf_text)} versus {len(prev_tpsf_text.rstrip())}")
        self.point_of_insc = PointOfInscription.END if len(prev_tpsf_text.rstrip()) <= ts.startpos <= len(prev_tpsf_text) else PointOfInscription.MID
        print(f"Point of insc is {self.point_of_insc}")
        self.sentence_segments = self._extract_segments()
        print(f"Sentence segments: {[(s.segment_type, s.length) for s in self.sentence_segments]}")
        self._verify_scope_based_on_segments()

    def _extract_segments(self) -> list[TextTransformationSegment]:
        if self.scope == TextTransScope.SEN:
            segments = [TextTransformationSegment(self.ts.text, SenSegmentTypes.SEN)]
        elif self.scope == TextTransScope.IN_SEN:
            for spsf in self.impacted_spsfs:
                if spsf.text_unit_type == 3 and self.ts.text.strip() != "":
                    text_to_search_for = self.ts.text.strip()
                    text_to_search_for = re.escape(text_to_search_for) ##
                    # text_to_search_for = text_to_search_for.replace("*", "\*")
                    # text_to_search_for = text_to_search_for.replace(".", "\.")
                    # text_to_search_for = text_to_search_for.replace("?", "\?")
                    # text_to_search_for = text_to_search_for.replace("(", "\(")
                    # text_to_search_for = text_to_search_for.replace(")", "\)")
                    print(f"text_to_search_for: {text_to_search_for}")
                    print(f"spsf.text: {spsf.text}")
                    ts_found = re.search(text_to_search_for, spsf.text)
                elif re.search(r"^\n|\t", self.ts.text):
                    ts_found = re.search(re.sub(r"^\n|\t", "", self.ts.text), spsf.text)
                else:
                    text_to_search_for = re.escape(self.ts.text) ##
                    # text_to_search_for = self.ts.text.replace("*", "\*")
                    # text_to_search_for = text_to_search_for.replace("(", "\(")
                    # text_to_search_for = text_to_search_for.replace(")", "\)")
                    print(f"text_to_search_for: *{text_to_search_for}*")
                    print(f"spsf.text: *{spsf.text}*")
                    ts_found = re.search(text_to_search_for, spsf.text)
                ts_start_position = None if not ts_found else ts_found.span()[0]
                ts_end_position = None if not ts_found else ts_found.span()[-1]
                print(f"Checking the spsf: |{spsf.text}| *** searching for text |{self.ts.text}| >>> ({ts_start_position} - {ts_end_position})")
                if ts_start_position == 0:
                    segments = [TextTransformationSegment(self.ts.text, SenSegmentTypes.SEN_BEG)]
                elif ts_end_position == len(spsf.text) and spsf.text_unit_type == 3:
                    segments = [TextTransformationSegment(self.ts.text, SenSegmentTypes.SEN_END)]
                elif ts_end_position == len(spsf.text) and spsf.text_unit_type == 2:
                    segments = [TextTransformationSegment(self.ts.text, SenSegmentTypes.SEN_MID)]
                elif spsf.text == self.ts.text:
                    segments = [TextTransformationSegment(self.ts.text, SenSegmentTypes.SEN_BEG)]
                else:
                    segments = [TextTransformationSegment(self.ts.text, SenSegmentTypes.SEN_MID)]
        else:
            segments = self._segment_ts()
        return segments

    def _segment_ts(self) -> list[TextTransformationSegment]:
        segments = []
        new_spsfs = [spsf for spsf in self.impacted_spsfs if spsf.state == "new"]
        # print(f"New spsfs: {[s.text for s in new_spsfs]}")
        ts_text = self.ts.text
        for nspsf in new_spsfs:
            ts_text = ts_text.replace(nspsf.text.strip(), "").strip()
        for spsf in self.impacted_spsfs:
            if spsf.state == "modified" and spsf.text.find(ts_text) == 0:
                segment = TextTransformationSegment(ts_text, SenSegmentTypes.SEN_BEG)
                segments.append(segment)
            elif spsf.state == "modified" and spsf.text.find(ts_text) > 0 and spsf.text_unit_type == 3:
                segment = TextTransformationSegment(ts_text, SenSegmentTypes.SEN_END)
                segments.append(segment)
            elif spsf.state == "modified" and spsf.text.find(ts_text) > 0 and spsf.text_unit_type == 2:
                segment = TextTransformationSegment(ts_text, SenSegmentTypes.SEN_MID)
                segments.append(segment)
            elif spsf.state == "new" and spsf.text_unit_type == 2:
                segment_content = spsf.text if spsf.text in self.ts.text else self._check_segment_content(spsf.text)
                segment = TextTransformationSegment(segment_content, SenSegmentTypes.SEN_BEG)
                segments.append(segment)
            elif spsf.state == "new" and spsf.text_unit_type == 3:
                segment = TextTransformationSegment(spsf.text, SenSegmentTypes.SEN)
                segments.append(segment)
        return segments

    def _check_segment_content(self, spsf_text: str) -> str:
        spsf_startpos = self.ts.text.find(spsf_text.strip())
        return self.ts.text[spsf_startpos:]


    def _verify_scope_based_on_segments(self) -> None:
        if len(self.sentence_segments) == 1 and self.sentence_segments[0].segment_type == SenSegmentTypes.SEN:
            self.scope = TextTransScope.SEN
        elif len(self.sentence_segments) == 1 and self.sentence_segments[0].segment_type in [SenSegmentTypes.SEN_BEG, SenSegmentTypes.SEN_END]:
            self.scope = TextTransScope.IN_SEN


class TextDelTransformation (TextTransformation):

    def __init__(
            self,
            tpsf_id: int,
            tpsf_text: str,
            scope: str,
            modified_spsfs: list[TextUnit],
            ts: TransformingSequence,
            prev_tpsf_text: str,
            deleted_spsfs: list[TextUnit],
            modified_spsfs_prev: list[TextUnit]
        ) -> None:
        super().__init__(tpsf_id, tpsf_text, scope, modified_spsfs, ts)
        print(f"{tpsf_id}: Calculating point of inscription for deletion: end at {ts.endpos}, prev_tpsf_textlen: {len(prev_tpsf_text)} versus {len(prev_tpsf_text.rstrip())}")
        self.point_of_insc = PointOfInscription.END if len(prev_tpsf_text.rstrip())-1 <= ts.endpos <= len(prev_tpsf_text)-1 else PointOfInscription.MID
        print(f"Point of insc is {self.point_of_insc}")
        self.deleted_spsfs = deleted_spsfs
        self.modified_spsfs_prev = modified_spsfs_prev
        self.sentence_segments = self._extract_segments()
        print(f"TS del segments: {[(s.segment_type, s.length) for s in self.sentence_segments]}")
        self._verify_scope_based_on_segments()

    def _extract_segments(self) -> list[TextTransformationSegment]:
        if self.scope == TextTransScope.SEN:
            segments = [TextTransformationSegment(self.ts.text, SenSegmentTypes.SEN)]
        elif self.scope == TextTransScope.IN_SEN:
            for spsf in self.modified_spsfs_prev:
                text_to_search_for = self.ts.text.strip()
                text_to_search_for = r"\." if text_to_search_for == "." else text_to_search_for
                ts_found = re.search(text_to_search_for, spsf.text) if text_to_search_for != "" else None
                ts_start_position = None if not ts_found else ts_found.span()[0]
                ts_end_position = None if not ts_found else ts_found.span()[-1]
                if ts_start_position == 0:
                    segments = [TextTransformationSegment(self.ts.text, SenSegmentTypes.SEN_BEG)]
                elif ts_end_position == len(spsf.text)  and spsf.text_unit_type == 3:
                    segments = [TextTransformationSegment(self.ts.text, SenSegmentTypes.SEN_END)]
                elif ts_end_position == len(spsf.text)  and spsf.text_unit_type == 2:
                    segments = [TextTransformationSegment(self.ts.text, SenSegmentTypes.SEN_MID)]
                elif ts_found is None:
                    segments = []
                else:
                    segments = [TextTransformationSegment(self.ts.text, SenSegmentTypes.SEN_MID)]
        else:
            segments = self._segment_ts()
        return segments

    def _segment_ts(self) -> list[TextTransformationSegment]:
        segments = []
        ts_text = self.ts.text
        for dspsf in self.deleted_spsfs:
            ts_text = ts_text.replace(dspsf.text.strip(), "").strip()
        for spsf in self.modified_spsfs_prev:
            if spsf.text.find(ts_text) == 0:
                segment = TextTransformationSegment(ts_text, SenSegmentTypes.SEN_BEG)
                segments.append(segment)
            elif spsf.text.find(ts_text) > 0:
                segment = TextTransformationSegment(ts_text, SenSegmentTypes.SEN_END)
                segments.append(segment)
            else:
                segment_text = ""
                spsf_text = spsf.text
                for token in ts_text.split(" "):
                    if token in spsf_text:
                        segment_text += f"{token} "
                        ts_text.replace(token, "")
                segment = TextTransformationSegment(segment_text.strip(), SenSegmentTypes.UNK)
                segments.append(segment)
        return segments

    def _verify_scope_based_on_segments(self) -> None:
        if len(self.sentence_segments) == 1 and self.sentence_segments[0].segment_type == SenSegmentTypes.SEN:
            self.scope = TextTransScope.SEN
        elif len(self.sentence_segments) == 1 and self.sentence_segments[0].segment_type in [SenSegmentTypes.SEN_BEG, SenSegmentTypes.SEN_END]:
            self.scope = TextTransScope.IN_SEN

class TextReplTransformation (TextTransformation):

    def __init__(
            self,
            tpsf_id: int,
            tpsf_text: str,
            scope: str,
            impacted_spsfs: list[TextUnit],
            ts: TransformingSequence,
            prev_tpsf_text: str,
            deleted_spsfs: list[TextUnit],
            modified_spsfs_prev: list[TextUnit],
            sequence_removed_by_repl: str | None
        ) -> None:
        super().__init__(tpsf_id, tpsf_text, scope, impacted_spsfs, ts)
        print(f"Calculating point of inscription for production: end at {ts.startpos + len(sequence_removed_by_repl) - 1}, prev_tpsf_textlen: {len(prev_tpsf_text)} versus {len(prev_tpsf_text.rstrip())}")
        self.point_of_insc = PointOfInscription.END if len(prev_tpsf_text.rstrip()) <= ts.startpos + len(sequence_removed_by_repl) - 1 <= len(prev_tpsf_text) else PointOfInscription.MID
        print(f"Point of insc is {self.point_of_insc}")
        self.deleted_spsfs = deleted_spsfs
        self.modified_spsfs_prev = modified_spsfs_prev
        self.sequence_removed_by_repl = sequence_removed_by_repl
        print(f"This is a replacement with scope {self.scope}.")
        print(f"This is the TS: |{ts.text}| ({ts.label})")
        print(f"This is the removed sequence: |{sequence_removed_by_repl}|")
        self.sentence_segments = self._extract_segments()
        print(f"TS replacement segments: {[(s.segment_type, s.length) for s in self.sentence_segments]}")
        self._verify_scope_based_on_segments()
        # self.subtransformations = self._split_into_subtransformations(ts, prev_tpsf_text)


    def _extract_segments(self) -> list[TextTransformationSegment]:
        if self.scope == TextTransScope.SEN:
            return [TextTransformationSegment(self.ts.text, SenSegmentTypes.SEN)]
        if self.scope == TextTransScope.IN_SEN:
            text_to_search_for = self.sequence_removed_by_repl.strip()
            if text_to_search_for == "":
                return []
            for spsf in self.modified_spsfs_prev:
                # print(f"Searching for the removed seq in |{spsf.text}|")
                text_to_search_for = r"\." if text_to_search_for == "." else text_to_search_for
                ts_found = re.search(text_to_search_for, spsf.text)
                ts_start_position = None if not ts_found else ts_found.span()[0]
                ts_end_position = None if not ts_found else ts_found.span()[-1]
                # print(f"Found: {ts_found}")
                if ts_found:
                    if ts_start_position == 0:
                        return [TextTransformationSegment(self.sequence_removed_by_repl, SenSegmentTypes.SEN_BEG)]
                    if ts_end_position == len(spsf.text) and spsf.text_unit_type == 3:
                        return [TextTransformationSegment(self.sequence_removed_by_repl, SenSegmentTypes.SEN_END)]
                    if ts_start_position and ts_end_position:
                        return [TextTransformationSegment(self.sequence_removed_by_repl, SenSegmentTypes.SEN_MID)]
        return self._segment_ts()

    def _segment_ts(self) -> list[TextTransformationSegment]:
        print("Trying to segment the TS...")
        segments = []
        ts_text = self.sequence_removed_by_repl
        for spsf in self.modified_spsfs_prev:
            if spsf in self.deleted_spsfs:
                if spsf.text_unit_type == 3:
                    segment = TextTransformationSegment(spsf.text, SenSegmentTypes.SEN)
                else:
                    ts_found = re.search(spsf.text.strip(), ts_text)
                    if ts_found and ts_found.span()[0] == 0:
                        segment = TextTransformationSegment(spsf.text, SenSegmentTypes.SEN_END)
                    if ts_found and ts_found.span()[-1] == len(ts_text)-1:
                        segment = TextTransformationSegment(spsf.text, SenSegmentTypes.SEN_BEG)
                    else:
                        segment = TextTransformationSegment(spsf.text, SenSegmentTypes.UNK)
                segments.append(segment)
                ts_text = ts_text.replace(spsf.text.strip(), "").strip()
            elif spsf.text.find(ts_text) == 0:
                segment = TextTransformationSegment(ts_text, SenSegmentTypes.SEN_BEG)
                segments.append(segment)
            elif spsf.text.find(ts_text) > 0:
                segment = TextTransformationSegment(ts_text, SenSegmentTypes.SEN_END)
                segments.append(segment)
            else:
                segment_text = ""
                spsf_text = spsf.text
                for token in ts_text.split(" "):
                    if token in spsf_text:
                        segment_text += f"{token} "
                        ts_text.replace(token, "")
                segment = TextTransformationSegment(segment_text.strip(), SenSegmentTypes.UNK)
                segments.append(segment)
            print(f"Segment: {segment.text}, {segment.segment_type}")
        return segments

    def _verify_scope_based_on_segments(self) -> None:
        if len(self.sentence_segments) == 1 and self.sentence_segments[0].segment_type == SenSegmentTypes.SEN:
            self.scope = TextTransScope.SEN
        elif len(self.sentence_segments) == 1 and self.sentence_segments[0].segment_type in [SenSegmentTypes.SEN_BEG, SenSegmentTypes.SEN_END]:
            self.scope = TextTransScope.IN_SEN

    # def _split_into_subtransformations(self, ts, prev_tpst_text) -> tuple[TextDelTransformation, TextProdTransformation]:
    #     del_transformation = TextDelTransformation(self.tpsf_id, self.tpsf_text, self.scope, self.impacted_spsfs, self.sequence_removed_by_repl, ts, prev_tpst_text, self.deleted_spsfs, self.modified_spsfs_prev)
    #     prod_transformation = TextProdTransformation(self.tpsf_id, self.scope, self.impacted_spsfs, ts.text, ts, self.tpsf_text, prev_tpst_text) if ts.text != "" else None
    #     return [del_transformation, prod_transformation] if prod_transformation else [del_transformation]
