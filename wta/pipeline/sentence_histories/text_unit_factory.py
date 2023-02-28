import re
from itertools import zip_longest
from typing import TYPE_CHECKING

import settings
from wta.pipeline.names import SenLabels, TSLabels
from wta.pipeline.text_history.ts import TransformingSequence

from ...utils.nlp import ends_with_end_punctuation, starts_with_uppercase_letter
from .. import regular_expressions
from .text_unit import Sec, Sen, Sin, TextUnit

if TYPE_CHECKING:
    from wta.pipeline.text_history.tpsf import TpsfECM


class TextUnitFactory:
    def run(
        self,
        text: str,
        revision_id: int,
        ts: TransformingSequence,
        prev_tpsf: "TpsfECM | None",
    ) -> tuple[list[TextUnit], list[str]]:
        print(
            f"\n\n=============================={revision_id}==============================\n"
        )
        sentence_list = settings.nlp_model.segment_text(text)
        textunit_list = self._split_in_textunits(sentence_list)
        merged_textunit_list = self._merge_double_textunits(textunit_list)
        pre_tus, changed_tus, post_tus = self._detect_tus_diffs(
            merged_textunit_list, ts, prev_tpsf
        )
        print(f"TS: {ts.label.upper()} ({ts.startpos}-{ts.endpos}): |{ts.text}|")
        print(f"TEXT: {text}")
        print(f"INITIAL SENTENCE LIST: {sentence_list}")
        corrected_changed_tus = self._improve_segmentation_with_post_tus(
            changed_tus, post_tus
        )
        tus_states = self._collect_tus_states(
            pre_tus, corrected_changed_tus, post_tus, ts
        )
        corrected_textunits = [*pre_tus, *corrected_changed_tus, *post_tus]
        final_tu_list = [
            (
                type(tu).__name__,
                tu.state if tu.state is None else tu.state.upper(),
                tu.text,
            )
            for tu in corrected_textunits
        ]
        print(f"FINAL TU LIST: {final_tu_list}")
        return corrected_textunits, tus_states

    def _split_in_textunits(self, sentence_list: list[str]) -> list[TextUnit]:
        textunit_list: list[TextUnit] = []
        for s in sentence_list:
            contains_only_ws = re.search(regular_expressions.ONLY_WS_RE, s) is not None
            if contains_only_ws is True:
                sin = Sin(s)
                textunit_list.append(sin)
                continue
            sen_wo_trailing_ws = re.sub(regular_expressions.TRAILING_WS_RE, "", s)
            if sen_wo_trailing_ws == "»":
                textunit_list[-1] = textunit_list[-1].copy_with_appended_text(
                    sen_wo_trailing_ws
                )
                sin_match = re.search(regular_expressions.TRAILING_WS_RE, s)
                if sin_match is not None:
                    textunit_list.append(Sin(sin_match.group(0)))
                continue
            sin_match = re.search(regular_expressions.INITIAL_WS_RE, s)
            if sin_match is not None:
                sin = Sin(sin_match.group(0))
                textunit_list.append(sin)
            sen_with_ws_trimmed = re.sub(
                regular_expressions.INITIAL_WS_RE, "", sen_wo_trailing_ws
            )
            uppercase_letter = starts_with_uppercase_letter(sen_with_ws_trimmed)
            end_punctuation = ends_with_end_punctuation(sen_with_ws_trimmed)
            if not uppercase_letter or not end_punctuation:
                s_wo_init_ws = re.sub(regular_expressions.INITIAL_WS_RE, "", s)
                sec = Sec(s_wo_init_ws)
                textunit_list.append(sec)
            else:
                sen = Sen(sen_with_ws_trimmed)
                textunit_list.append(sen)
                sin_match = re.search(regular_expressions.TRAILING_WS_RE, s)
                if sin_match is not None:
                    sin = Sin(sin_match.group(0))
                    textunit_list.append(sin)
        return textunit_list

    def _merge_double_textunits(self, textunit_list: list[TextUnit]) -> list[TextUnit]:
        if not any(
            type(i).__name__ == type(j).__name__ != "Sen"
            for (i, j) in zip_longest(textunit_list, textunit_list[1:])
        ):
            # print(f'No more doubles.')
            return textunit_list

        # print(f'Detected doubles. Need to merge.')
        prev_merged_text = ""
        merged_textunits = []
        for i, j in zip_longest(textunit_list, textunit_list[1:]):
            if type(i).__name__ == type(j).__name__ != "Sen":
                merged_tu_text = i.text + j.text
                text_wo_trailing_ws = re.sub(
                    regular_expressions.TRAILING_WS_RE, "", merged_tu_text
                )
                uppercase_letter = starts_with_uppercase_letter(text_wo_trailing_ws)
                end_punctuation = ends_with_end_punctuation(text_wo_trailing_ws)
                if not uppercase_letter or not end_punctuation:
                    merged_tu = i.copy_with_text(merged_tu_text)
                    merged_textunits.append(merged_tu)
                else:
                    sen = Sen(text_wo_trailing_ws)
                    merged_textunits.append(sen)
                    sin_content = merged_tu_text.replace(text_wo_trailing_ws, "")
                    if len(sin_content) > 0:
                        sin = Sin(sin_content)
                        merged_textunits.append(sin)
                prev_merged_text = j.text
            elif i.text != prev_merged_text:
                merged_textunits.append(i)
                prev_merged_text = ""
        return self._merge_double_textunits(merged_textunits)

    def _detect_tus_diffs(
        self,
        textunits: list[TextUnit],
        ts: TransformingSequence,
        prev_tpsf: "TpsfECM | None",
    ) -> tuple[list[TextUnit], list[TextUnit], list[TextUnit]]:
        if ts.label in [TSLabels.MID, TSLabels.DEL, TSLabels.REPL]:
            prev_textunits: list[TextUnit] = (
                [] if prev_tpsf is None else prev_tpsf.textunits
            )
            pre_tus, changed_tus, post_tus = self._check_what_changed(
                prev_textunits, ts
            )
            # if the edit consists in deleting or reducing sentence interspace
            if (
                len(changed_tus) == 1
                and type(changed_tus[0]).__name__ == "Sin"
                and ts.label in (TSLabels.MID, TSLabels.DEL)
            ):
                reduced_sin_content = re.sub(ts.text, "", changed_tus[0].text, count=1)
                if reduced_sin_content == "":
                    changed_tus = []
                else:
                    match = re.search(
                        regular_expressions.ONLY_WS_RE, reduced_sin_content
                    )
                    if match is not None:
                        sin_content = match.group(0)
                        changed_tus = [Sin(sin_content)]
            else:
                changed_tus = [
                    tu
                    for tu in textunits
                    if tu.text
                    not in [
                        *[prtu.text for prtu in pre_tus],
                        *[potu.text for potu in post_tus],
                    ]
                ]
        elif ts.label in [TSLabels.APP, TSLabels.INS, TSLabels.PAST]:
            pre_tus, changed_tus, post_tus = self._check_what_changed(textunits, ts)
        return pre_tus, changed_tus, post_tus

    def _check_what_changed(
        self, tus: list[TextUnit], ts: TransformingSequence
    ) -> tuple[list[TextUnit], list[TextUnit], list[TextUnit]]:
        pre_tus = []
        post_tus = []
        changed_tus = []
        currentpos = 0
        for tu in tus:
            startpos, endpos = currentpos, currentpos + len(tu.text) - 1
            if endpos < ts.startpos:
                pre_tus.append(tu)
            elif ts.endpos is not None and startpos > ts.endpos:
                post_tus.append(tu)
            else:
                changed_tus.append(tu)
            currentpos = currentpos + len(tu.text)
        return pre_tus, changed_tus, post_tus

    def _improve_segmentation_with_post_tus(
        self, changed_tus: list[TextUnit], post_tus: list[TextUnit]
    ) -> list[TextUnit]:
        post_sens = [ptu for ptu in post_tus if type(ptu).__name__ == "Sen"]
        corrected_changed_tus: list[TextUnit] = []
        for ctu in changed_tus:
            matching_sens = [
                psen for psen in post_sens if re.search(psen.text, ctu.text) is not None
            ]
            if len(matching_sens) == 1:
                matching_sen = matching_sens[0]
                new_ctu_text = re.sub(matching_sen.text, "", ctu.text)
                uppercase_letter = starts_with_uppercase_letter(new_ctu_text)
                end_punctuation = ends_with_end_punctuation(new_ctu_text)
                if not uppercase_letter or not end_punctuation:
                    sec = Sec(new_ctu_text)
                    corrected_changed_tus.append(sec)
                else:
                    sen = Sen(
                        re.sub(regular_expressions.TRAILING_WS_RE, "", new_ctu_text)
                    )
                    corrected_changed_tus.append(sen)
                    match = re.search(regular_expressions.TRAILING_WS_RE, new_ctu_text)
                    sin_content = None if match is None else match.group(0)
                    if sin_content is not None:
                        sin = Sin(sin_content)
                        corrected_changed_tus.append(sin)
            elif len(matching_sens) == 0:
                corrected_changed_tus.append(ctu)
            else:
                print(
                    f"ATTENTION: {len(matching_sens)} textunits have been found within the textunit {ctu.text}"
                )
        return corrected_changed_tus

    def _collect_tus_states(
        self,
        pre_tus: list[TextUnit],
        changed_tus: list[TextUnit],
        post_tus: list[TextUnit],
        ts: TransformingSequence,
    ) -> list[str]:
        tus_states = []
        currentpos = 0
        for tu in [*pre_tus, *changed_tus, *post_tus]:
            state = self._collect_tus_state(tu, currentpos, pre_tus, post_tus, ts)
            if state is not None:
                tu.set_state(state)
                tus_states.append(state)
            currentpos = currentpos + len(
                tu.text
            )  # it's the index of the beginning of the next tu
        return tus_states

    def _collect_tus_state(
        self,
        tu: TextUnit,
        currentpos: int,
        pre_tus: list[TextUnit],
        post_tus: list[TextUnit],
        ts: TransformingSequence,
    ) -> str | None:
        if len(tu.text) == 0:
            return None

        if ts.endpos is None:
            msg = f"The TransformingSequence should have an endpos: {ts}"
            raise ValueError(msg)

        startpos, endpos = currentpos, currentpos + len(tu.text) - 1
        tu_starts_within_ts = startpos in range(ts.startpos, ts.endpos + 1)
        tu_ends_within_ts = endpos in range(ts.startpos, ts.endpos + 1)
        if tu in pre_tus:
            return SenLabels.UNC_PRE

        if tu in post_tus:
            return SenLabels.UNC_POST

        if (
            ts.label in [TSLabels.INS, TSLabels.APP, TSLabels.PAST]
            and tu_starts_within_ts
            and tu_ends_within_ts
        ):
            return SenLabels.NEW

        return SenLabels.MOD
