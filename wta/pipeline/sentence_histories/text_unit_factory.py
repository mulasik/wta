import re
from typing import TYPE_CHECKING

from ...pipeline.names import SenLabels, TSLabels
from ...pipeline.text_history.ts import TransformingSequence
from ...settings import Settings
from ...utils.nlp import ends_with_end_punctuation, starts_with_uppercase_letter
from .. import regular_expressions
from .text_unit import TextUnit, TextUnitBuilder, TextUnitType

if TYPE_CHECKING:
    from ..text_history.tpsf import TpsfECM


class TextUnitFactory:
    def run(
        self,
        text: str,
        revision_id: int,
        ts: TransformingSequence,
        prev_tpsf: "TpsfECM | None",
        settings: Settings,
    ) -> tuple[TextUnit, ...]:
        """
        Generate a list of textunits for the given TPSF.
        """

        sentence_list = settings.nlp_model.segment_text(text)

        textunit_list = self._split_in_textunits(sentence_list)

        merged_textunit_list = self._merge_double_textunits(textunit_list)

        # print(
        #     f"\n\n=============================={revision_id}==============================\n"
        # )
        # print(f"TS: {ts.label.upper()} ({ts.startpos}-{ts.endpos}): |{ts.text}|\n")
        # print(f"Text segment impacted by the TS: |{text[ts.startpos:ts.endpos+1]}|")
        # print(f"TEXT: {text}")
        # print(f"\nINITIAL SENTENCE LIST: {sentence_list}\n")
        # print(
        #     f"\nINITIAL TEXTUNITS: {[(tu.text, tu.text_unit_type) for tu in textunit_list]}\n"
        # )
        # print(f"\nTUs after merging: {[tu.text for tu in merged_textunit_list]}\n")

        corrected_tus = self._improve_segmentation_with_prev_tus(
            merged_textunit_list, prev_tpsf
        )

        # print(f"\nCorrected TUs: {[tu.text for tu in corrected_tus]}\n")

        # collect TU states
        pre_tus, impacted_tus, post_tus = self._detect_diffs(
            corrected_tus, ts, prev_tpsf
        )

        # print(f"\nImpacted TUs: {[tu.text for tu in impacted_tus]}\n")

        self._set_tus_states(pre_tus, impacted_tus, post_tus, ts, prev_tpsf)

        tus = [*pre_tus, *impacted_tus, *post_tus]

        self._assign_tpsf_ids(tus, revision_id)

        # TODO remove final_tu_list var after testing
        final_tu_list = [  # noqa: F841
            (
                tu.text_unit_type,
                tu.state if tu.state is None else tu.state.upper(),
                tu.text,
            )
            for tu in tus
        ]
        # print(f"FINAL TU LIST: {final_tu_list}\n")

        return tuple(tu.to_text_unit() for tu in tus)

    def _split_in_textunits(self, sentence_list: list[str]) -> list[TextUnitBuilder]:
        textunit_list: list[TextUnitBuilder] = []

        for s in sentence_list:
            contains_only_ws = regular_expressions.ONLY_WS_RE.search(s) is not None
            if contains_only_ws is True:
                sin = TextUnitBuilder(TextUnitType.SIN, s)
                textunit_list.append(sin)
                continue

            # Handling special cases: incorrect SpaCy segmentation in case of citations with «»
            # sentence returned by SpaCy starts with end citation mark (which should be part of the previous sentence)
            found_end_citation_at_beginning = re.search(r"\A»", s)
            if found_end_citation_at_beginning is not None:
                textunit_list[-1] = textunit_list[-1].copy_with_appended_text("»")
                s = re.sub(r"\A»", "", s)

            found_initial_sin = regular_expressions.INITIAL_WS_RE.search(s)
            if found_initial_sin is not None:
                sin = TextUnitBuilder(TextUnitType.SIN, found_initial_sin.group(0))
                textunit_list.append(sin)
                s = s.replace(found_initial_sin.group(0), "")

            middle_sins = regular_expressions.MIDDLE_WS_RE.findall(s)
            print(middle_sins)
            middle_sin_matches = []
            for middle_sin_tup in middle_sins:
                match = [t for t in middle_sin_tup if t != ""][0]
                middle_sin_matches.append(match)
            if middle_sin_matches != []:
                print(middle_sin_matches)
                for middle_sin in middle_sin_matches:
                    print(f"Found middle sin: |{middle_sin}|")
                    split_sens = s.split(middle_sin, 1)
                    print(f"There are {len(split_sens)} SPSFs in this sequence split by middle SIN:")
                    first_sen = split_sens[0]
                    second_sen = "" if len(split_sens) == 1 else split_sens[1]
                    print(f"first_sen: {first_sen}")
                    print(f"second_sen: {second_sen}")
                    first_sen_with_ws_trimmed = regular_expressions.TRAILING_WS_RE.sub("", first_sen)
                    if first_sen_with_ws_trimmed != "":
                        uppercase_letter = starts_with_uppercase_letter(first_sen_with_ws_trimmed)
                        end_punctuation = ends_with_end_punctuation(first_sen_with_ws_trimmed)
                        if not uppercase_letter or not end_punctuation:
                            print(f"First SPSF before SIN is a SEC: |{first_sen_with_ws_trimmed}|")
                            second_sen_with_ws_trimmed = regular_expressions.TRAILING_WS_RE.sub("", second_sen)
                            uppercase_letter_sec = starts_with_uppercase_letter(second_sen_with_ws_trimmed)
                            end_punctuation_sec = ends_with_end_punctuation(second_sen_with_ws_trimmed)
                            sec_content = s if not uppercase_letter_sec or not end_punctuation_sec else first_sen + middle_sin
                            print(f"This is the content of the SEC: |{sec_content}|")
                            sec = TextUnitBuilder(TextUnitType.SEC, sec_content)
                            textunit_list.append(sec)
                            s = "" if sec_content == s else second_sen
                            if s == "":
                                break
                        else:
                            print(f"First SPSF before SIN is a SEN: |{first_sen_with_ws_trimmed}|")
                            sen = TextUnitBuilder(TextUnitType.SEN, first_sen_with_ws_trimmed)
                            textunit_list.append(sen)
                            found_trailing_ws = regular_expressions.TRAILING_WS_RE.search(first_sen)
                            trailing_ws = "" if found_trailing_ws is None else found_trailing_ws.group(0)
                            sin_content = f"{trailing_ws}{middle_sin}"
                            print(f"Added a SIN after the SEN: |{sin_content}|")
                            sin = TextUnitBuilder(TextUnitType.SIN, sin_content)
                            textunit_list.append(sin)
                            s = second_sen
                    else:
                        sin = TextUnitBuilder(TextUnitType.SIN, middle_sin)
                        textunit_list.append(sin)
                        s = second_sen
            print(f"After checking middle SIN, I ended up with the following SPSF: |{s}|")

            sen_with_ws_trimmed = regular_expressions.TRAILING_WS_RE.sub("", s)
            if sen_with_ws_trimmed != "":
                uppercase_letter = starts_with_uppercase_letter(sen_with_ws_trimmed)
                end_punctuation = ends_with_end_punctuation(sen_with_ws_trimmed)
                if not uppercase_letter or not end_punctuation:
                    sec = TextUnitBuilder(TextUnitType.SEC, s)
                    textunit_list.append(sec)
                else:
                    sen = TextUnitBuilder(TextUnitType.SEN, sen_with_ws_trimmed)
                    textunit_list.append(sen)
                    found_initial_sin = regular_expressions.TRAILING_WS_RE.search(s)
                    if found_initial_sin is not None:
                        sin = TextUnitBuilder(
                            TextUnitType.SIN, found_initial_sin.group(0)
                        )
                        textunit_list.append(sin)

        return textunit_list

    def _merge_double_textunits(
        self, textunit_list: list[TextUnitBuilder]
    ) -> list[TextUnitBuilder]:
        # TODO: Issue with merging: 'So hat sie eine Qualt\n\nDie Qualitätsstrategie ', 'Die Qualitätsstrategie
        if not any(
            i.text_unit_type == j.text_unit_type != TextUnitType.SEN
            for (i, j) in zip(textunit_list, textunit_list[1:])
        ):
            # print(f'No more doubles.')
            return textunit_list

        # print(f'Detected doubles. Need to merge.')
        prev_merged_text = ""
        merged_textunits = []
        merged = False
        for i, j in zip(textunit_list, textunit_list[1:]):
            if (
                i.text_unit_type == j.text_unit_type != TextUnitType.SEN
                and i.text != prev_merged_text
            ):
                merged_tu_text = i.text + j.text
                text_wo_trailing_ws = regular_expressions.TRAILING_WS_RE.sub(
                    "", merged_tu_text
                )
                uppercase_letter = starts_with_uppercase_letter(text_wo_trailing_ws)
                end_punctuation = ends_with_end_punctuation(text_wo_trailing_ws)
                if not uppercase_letter or not end_punctuation:
                    merged_tu = i.copy_with_text(merged_tu_text)
                    merged_textunits.append(merged_tu)
                else:
                    sen = TextUnitBuilder(TextUnitType.SEN, text_wo_trailing_ws)
                    merged_textunits.append(sen)
                    sin_content = merged_tu_text.replace(text_wo_trailing_ws, "")
                    if len(sin_content) > 0:
                        sin = TextUnitBuilder(TextUnitType.SIN, sin_content)
                        merged_textunits.append(sin)
                prev_merged_text = j.text
                merged = True
            elif i.text != prev_merged_text:
                merged_textunits.append(i)
                prev_merged_text = ""
                merged = False
        if merged is False:
            merged_textunits.append(j)
        return self._merge_double_textunits(merged_textunits)

    def _improve_segmentation_with_prev_tus(
        self, tus: list[TextUnitBuilder], prev_tpsf: "TpsfECM | None"
    ) -> list[TextUnitBuilder]:
        prev_sens = (
            []
            if prev_tpsf is None
            else [
                ptu.copy_to_builder()
                for ptu in prev_tpsf.textunits
                if ptu.text_unit_type == TextUnitType.SEN
            ]
        )
        corrected_tus: list[TextUnitBuilder] = []

        for tu in tus:
            matching_prev_sens = [
                psen for psen in prev_sens if psen.text in tu.text
            ]  # is any previous sentence part of the detected text unit?
            if len(matching_prev_sens) == 1:
                matching_sen = matching_prev_sens[0]
                matching_sen_index = tu.text.find(matching_sen.text)
                if matching_sen_index == 0:
                    corrected_tus.append(matching_sen)
                new_ctu_text = tu.text.replace(matching_sen.text, "")
                if new_ctu_text != "":
                    preceding_whitespace = regular_expressions.INITIAL_WS_RE.search(new_ctu_text)
                    if preceding_whitespace is not None:
                        preceding_sin_content = preceding_whitespace.group(0)
                        sin = TextUnitBuilder(TextUnitType.SIN, preceding_sin_content)
                        corrected_tus.append(sin)
                        new_ctu_text = new_ctu_text.replace(preceding_sin_content, "")
                    uppercase_letter = starts_with_uppercase_letter(new_ctu_text)
                    end_punctuation = ends_with_end_punctuation(new_ctu_text)
                    if not uppercase_letter or not end_punctuation:
                        sec = TextUnitBuilder(TextUnitType.SEC, new_ctu_text)
                        corrected_tus.append(sec)
                    else:
                        sen = TextUnitBuilder(
                            TextUnitType.SEN,
                            regular_expressions.TRAILING_WS_RE.sub("", new_ctu_text),
                        )
                        corrected_tus.append(sen)
                        match = regular_expressions.TRAILING_WS_RE.search(new_ctu_text)
                        sin_content = None if match is None else match.group(0)
                        if sin_content is not None:
                            sin = TextUnitBuilder(TextUnitType.SIN, sin_content)
                            corrected_tus.append(sin)
                if matching_sen_index > 0:

                    corrected_tus.append(matching_sen)
            elif len(matching_prev_sens) == 0:
                corrected_tus.append(tu)
            else:
                print(
                    f"ATTENTION: {len(matching_prev_sens)} textunits have been found within the textunit {tu.text}"
                )
        return corrected_tus

    def _detect_diffs(
        self,
        textunits: list[TextUnitBuilder],
        ts: TransformingSequence,
        prev_tpsf: "TpsfECM | None",
    ) -> tuple[list[TextUnitBuilder], list[TextUnitBuilder], list[TextUnitBuilder]]:
        prev_textunits: list[TextUnitBuilder] = (
                []
                if prev_tpsf is None
                else [tu.copy_to_builder() for tu in prev_tpsf.textunits]
            )
        if ts.label in [TSLabels.MID, TSLabels.DEL, TSLabels.REPL]:
            pre_tus, impacted_tus, post_tus = self._check_what_is_impacted(
                textunits, prev_textunits, ts
            )
            # if the edit consists in deleting or reducing sentence interspace
            if (
                len(impacted_tus) == 1
                and impacted_tus[0].text_unit_type == TextUnitType.SIN
                and ts.label in (TSLabels.MID, TSLabels.DEL)
            ):
                reduced_sin_content = impacted_tus[0].text.replace(ts.text, "", 1)
                if reduced_sin_content == "":
                    impacted_tus = []
                else:
                    match = regular_expressions.ONLY_WS_RE.search(reduced_sin_content)
                    if match is not None:
                        sin_content = match.group(0)
                        impacted_tus = [TextUnitBuilder(TextUnitType.SIN, sin_content)]
            else:
                impacted_tus = [
                    tu
                    for tu in textunits
                    if tu.text
                    not in [
                        *[prtu.text for prtu in pre_tus],
                        *[potu.text for potu in post_tus],
                    ]
                ]
        elif ts.label in [TSLabels.APP, TSLabels.INS, TSLabels.PAST]:
            pre_tus, impacted_tus, post_tus = self._check_what_is_impacted(
                prev_textunits, textunits, ts
            )
        return pre_tus, impacted_tus, post_tus

    def _check_what_is_impacted(
        self, textunits_to_compare_with: list[TextUnitBuilder], tus_potentially_impacted: list[TextUnitBuilder], ts: TransformingSequence
    ) -> tuple[list[TextUnitBuilder], list[TextUnitBuilder], list[TextUnitBuilder]]:
        pre_tus = []
        post_tus = []
        impacted_tus = []
        currentpos = 0
        # print("Checking impacted TUs...")
        for tu in tus_potentially_impacted:
            startpos, endpos = currentpos, currentpos + len(tu.text) - 1
            # print(f"Text unit: |{tu}|")
            # print(startpos, endpos)
            # print(ts.startpos, ts.endpos)
            if endpos < ts.startpos and tu.text in [tu.text for tu in textunits_to_compare_with]:
                pre_tus.append(tu)
            elif ts.endpos is not None and startpos > ts.endpos and tu.text in [tu.text for tu in textunits_to_compare_with]:
                post_tus.append(tu)
            else:
                impacted_tus.append(tu)
            currentpos = currentpos + len(tu.text)
        return pre_tus, impacted_tus, post_tus

    def _set_tus_states(
        self,
        pre_tus: list[TextUnitBuilder],
        impacted_tus: list[TextUnitBuilder],
        post_tus: list[TextUnitBuilder],
        ts: TransformingSequence,
        prev_tpsf: "TpsfECM | None",
    ) -> None:
        currentpos = 0
        prev_tus = (
            []
            if prev_tpsf is None
            else [tu.copy_to_builder() for tu in prev_tpsf.textunits]
        )
        no_tus_increased = len(prev_tus) < len([*pre_tus, *impacted_tus, *post_tus])
        for tu in [*pre_tus, *impacted_tus, *post_tus]:
            state = self._retrieve_tu_state(
                tu, currentpos, pre_tus, post_tus, ts, prev_tus, no_tus_increased
            )
            if state is not None:
                tu.set_state(state)
            currentpos = currentpos + len(
                tu.text
            )  # it's the index of the beginning of the next tu

    def _retrieve_tu_state(
        self,
        tu: TextUnitBuilder,
        currentpos: int,
        pre_tus: list[TextUnitBuilder],
        post_tus: list[TextUnitBuilder],
        ts: TransformingSequence,
        prev_tus: list[TextUnitBuilder],
        no_tus_increased: bool,
    ) -> str | None:
        if len(tu.text) == 0:
            return None

        if ts.endpos is None:
            msg = f"The TransformingSequence should have an endpos: {ts}"
            raise ValueError(msg)

        startpos, endpos = currentpos, currentpos + len(tu.text) - 1
        tu_starts_within_ts = startpos in range(ts.startpos, ts.endpos + 1)
        # two options in case the textunit ends with space
        # if it ends with space this space might have previously build a SIN, but as a SEC has been inserted
        # the SIN became part of the SEC as per definition (see Languages paper)
        trailing_ws_match = re.search(r"\s+$", tu.text)
        no_trailing_ws = (
            0 if trailing_ws_match is None else len(trailing_ws_match.group(0))
        )
        tu_ends_within_ts = endpos in range(ts.startpos, ts.endpos + 1 + no_trailing_ws)

        if tu in pre_tus:
            return SenLabels.UNC_PRE

        if tu in post_tus and tu.text in [t.text for t in prev_tus]:
            return SenLabels.UNC_POST

        if tu in post_tus and tu.text not in [t.text for t in prev_tus]:
            return SenLabels.SPLIT

        if (
            ts.label in [TSLabels.INS, TSLabels.APP, TSLabels.PAST]
            and tu_starts_within_ts
            and tu_ends_within_ts
        ):
            return SenLabels.NEW

        if no_tus_increased is True:
            # check if tu without the ts was is prev tus list
            # then the status is "split"
            ts_split_by_tu = re.split(r"(\.|\?|!)", ts.text)
            ts_first_tu = "".join(ts_split_by_tu[:2])
            tu_wo_ts = tu.text.replace(ts_first_tu, "")
            tu_wo_ts_found_in_prev = False
            for i, ptu in enumerate(prev_tus):
                if tu_wo_ts in ptu.text:
                    tu_wo_ts_found_in_prev = True
                    last_prev_tu = i == len(prev_tus) - 1
                    break
            if tu_wo_ts_found_in_prev and not last_prev_tu:
                return SenLabels.SPLIT

        return SenLabels.MOD

    def _assign_tpsf_ids(self, tus: list[TextUnitBuilder], revision_id: int) -> None:
        for tu in tus:
            tu.set_tpsf_id(revision_id)
