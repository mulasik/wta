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

        print(
            f"\n\n=============================={revision_id}==============================\n"
        )
        print(f"TS: {ts.label.upper()} ({ts.startpos}-{ts.endpos}): |{ts.text}|\n")
        print(f"Text segment impacted by the TS: |{text[ts.startpos:ts.endpos+1]}|")
        print(f"TEXT: {text}")
        print(f"\nINITIAL SENTENCE LIST: {sentence_list}\n")

        textunit_list = self._split_in_textunits(sentence_list)

        merged_textunit_list = self._merge_double_textunits(textunit_list)

        print(
            f"\nINITIAL TEXTUNITS: {[(tu.text, tu.text_unit_type) for tu in textunit_list]}\n"
        )
        print(f"\nTUs after merging: {[tu.text for tu in merged_textunit_list]}\n")

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

    def collect_preceding_sins_and_pins(self, seq: str, textunit_list: list[TextUnitBuilder]) -> tuple[str, list[TextUnitBuilder]]:
        starts_with_s = regular_expressions.PRECEDING_S_RE.search(seq)
        starts_with_pws = regular_expressions.PRECEDING_PWS_RE.search(seq)
        if starts_with_s is not None:
            sin_content = starts_with_s.group(0)
            sin = TextUnitBuilder(TextUnitType.SIN, sin_content)
            textunit_list.append(sin)
            seq = re.sub(sin_content, "", seq)
        elif starts_with_pws is not None:
            pin_content = starts_with_pws.group(0)
            pin = TextUnitBuilder(TextUnitType.PIN, pin_content)
            textunit_list.append(pin)
            seq = re.sub(pin_content, "", seq)
        else:
            return seq, textunit_list
        return self.collect_preceding_sins_and_pins(seq, textunit_list)

    def find_middle_pins(self, seq: str) -> list[str]:
        middle_pins = regular_expressions.MIDDLE_PWS_RE.findall(seq)
        middle_pin_matches = []
        for middle_pin_tup in middle_pins:
            match = [t for t in middle_pin_tup if t != ""][0]
            middle_pin_matches.append(match)
        return middle_pin_matches

    def split_tu_by_pins(self, seq: str, textunit_list: list[TextUnitBuilder], middle_pins: list[str]) -> tuple[str, list[TextUnitBuilder]]:
        if middle_pins == []:
            return seq, textunit_list
        middle_pin = middle_pins.pop(0)
        print(f"Splitting by the PIN: |{middle_pin}|")
        split_tus = seq.split(middle_pin, 1)
        print(f"There are {len(split_tus)} TUs in this sequence split by middle PIN:")
        first_tu = split_tus[0]
        second_tu = "" if len(split_tus) == 1 else split_tus[1]
        print(f"First TU: |{first_tu}|")
        print(f"Second TU: |{second_tu}|")
        _, textunit_list = self.retrieve_sen_or_sec(first_tu, textunit_list)
        pin = TextUnitBuilder(TextUnitType.PIN, middle_pin)
        textunit_list.append(pin)
        return self.split_tu_by_pins(second_tu, textunit_list, middle_pins)

    def trim_trailing_sins_and_pins(self, seq: str) -> str:
        ends_with_s = regular_expressions.TRAILING_S_RE.search(seq)
        ends_with_pws = regular_expressions.TRAILING_PWS_RE.search(seq)
        if ends_with_s is not None:
            seq = re.sub(regular_expressions.TRAILING_S_RE, "", seq)
        elif ends_with_pws is not None:
            seq = re.sub(regular_expressions.TRAILING_PWS_RE, "", seq)
        else:
            return seq
        return self.trim_trailing_sins_and_pins(seq)

    def collect_trailing_sins_and_pins(self, seq: str, textunit_list: list[TextUnitBuilder]) -> tuple[str, list[TextUnitBuilder]]:
        ends_with_s = regular_expressions.TRAILING_S_RE.search(seq)
        ends_with_pws = regular_expressions.TRAILING_PWS_RE.search(seq)
        if ends_with_s is not None:
            sin_content = ends_with_s.group(0)
            sin = TextUnitBuilder(TextUnitType.SIN, sin_content)
            textunit_list.append(sin)
            seq = re.sub(sin_content, "", seq)
        elif ends_with_pws is not None:
            pin_content = ends_with_pws.group(0)
            pin = TextUnitBuilder(TextUnitType.PIN, pin_content)
            textunit_list.append(pin)
            seq = re.sub(pin_content, "", seq)
        else:
            # seq should be empty after the function is executed
            return seq, textunit_list
        return self.collect_trailing_sins_and_pins(seq, textunit_list)

    def retrieve_sen_or_sec(self, seq: str, textunit_list: list[TextUnitBuilder]) -> tuple[str, list[TextUnitBuilder]]:
        # if the seq contains only space characters, no SEN or SEC can be retrieved
        if re.search(regular_expressions.ONLY_S_RE, seq) is not None:
            return seq, textunit_list
        seq_with_whitespaces_trimmed = self.trim_trailing_sins_and_pins(seq)
        uppercase_letter = starts_with_uppercase_letter(seq_with_whitespaces_trimmed)
        end_punctuation = ends_with_end_punctuation(seq_with_whitespaces_trimmed)
        if not uppercase_letter or not end_punctuation and re.search(regular_expressions.ONLY_S_RE, seq) is None:
            sec = TextUnitBuilder(TextUnitType.SEC, seq)
            textunit_list.append(sec)
            seq = ""
        else:
            sen = TextUnitBuilder(TextUnitType.SEN, seq_with_whitespaces_trimmed)
            textunit_list.append(sen)
            seq = re.sub(seq_with_whitespaces_trimmed, "", seq)
            seq, textunit_list = self.collect_trailing_sins_and_pins(seq, textunit_list)
        # seq should be empty after the function is executed
        return seq, textunit_list

    def _split_in_textunits(self, sentence_list: list[str]) -> list[TextUnitBuilder]:
        textunit_list: list[TextUnitBuilder] = []

        for s in sentence_list:

            # print(f"\n\n\n\n****** Analysing sentence:\n|{s}|\n******")

            # check if s contains only space chars > SIN
            contains_only_s = regular_expressions.ONLY_S_RE.search(s)
            if contains_only_s is not None:
                sin = TextUnitBuilder(TextUnitType.SIN, s)
                textunit_list.append(sin)
                continue

            # check if s contains only paragraph whitespace chars > PIN
            contains_only_pws = regular_expressions.ONLY_PWS_RE.search(s)
            if contains_only_pws is not None:
                pin = TextUnitBuilder(TextUnitType.PIN, s)
                textunit_list.append(pin)
                continue

            # Handling special cases: incorrect SpaCy segmentation in case of citations with «»
            # sentence returned by SpaCy starts with end citation mark (which should be part of the previous sentence)
            found_end_citation_at_beginning = re.search(r"\A»", s)
            if found_end_citation_at_beginning is not None:
                textunit_list[-1] = textunit_list[-1].copy_with_appended_text("»")
                s = re.sub(regular_expressions.PRECEDING_END_CITATION, "", s)

            s, textunit_list = self.collect_preceding_sins_and_pins(s, textunit_list)
            middle_pins = self.find_middle_pins(s)
            print(f"Found middle pins: {middle_pins} in |{s}|")
            s, textunit_list = self.split_tu_by_pins(s, textunit_list, middle_pins)
            print(f"I am now left with |{s}|")
            if s != "":
                s, textunit_list = self.retrieve_sen_or_sec(s, textunit_list)
                print(f"After retrieving SEN or SEC I got: |{s}|")
            if s != "":
                s, textunit_list = self.collect_trailing_sins_and_pins(s, textunit_list)
                print(f"After trailing SINs and PINs I got: |{s}|")

        return textunit_list

    def _merge_double_textunits(
        self, textunit_list: list[TextUnitBuilder]
    ) -> list[TextUnitBuilder]:
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
            print("\n\nComparing")
            print(f"|{i.text}|")
            print("with")
            print(f"|{j.text}|")
            if (
                i.text_unit_type == j.text_unit_type != TextUnitType.SEN
                and i.text != prev_merged_text
            ):
                merged_tu_text = i.text + j.text
                text_wo_trailing_ws = self.trim_trailing_sins_and_pins(merged_tu_text)
                uppercase_letter = starts_with_uppercase_letter(text_wo_trailing_ws)
                end_punctuation = ends_with_end_punctuation(text_wo_trailing_ws)
                if not uppercase_letter or not end_punctuation:
                    merged_tu = i.copy_with_text(merged_tu_text)
                    merged_textunits.append(merged_tu)
                else:
                    sen = TextUnitBuilder(TextUnitType.SEN, text_wo_trailing_ws)
                    merged_textunits.append(sen)
                    remaining_content = merged_tu_text.replace(text_wo_trailing_ws, "")
                    _, merged_textunits = self.collect_trailing_sins_and_pins(remaining_content, merged_textunits)
                prev_merged_text = j.text
                merged = True
                print(f"I have merged: |{merged_tu_text}|")
                print(f"Merge flag: {merged}")
                print(f"Prev merged text is: |{prev_merged_text}|")
            elif i.text != prev_merged_text:
                merged_textunits.append(i)
                prev_merged_text = ""
                merged = False
                print(f"I have NOT merged: |{i.text}|")
                print(f"Merge flag: {merged}")
                print(f"Prev merged text is: |{prev_merged_text}|")
        if j.text != prev_merged_text:
            print(f"I have added |{j.text}| to text units list")
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
                    uppercase_letter = starts_with_uppercase_letter(new_ctu_text)
                    end_punctuation = ends_with_end_punctuation(new_ctu_text)
                    if not uppercase_letter or not end_punctuation:
                        sec = TextUnitBuilder(TextUnitType.SEC, new_ctu_text)
                        corrected_tus.append(sec)
                    else:
                        sen = TextUnitBuilder(
                            TextUnitType.SEN,
                            regular_expressions.TRAILING_S_RE.sub("", new_ctu_text),
                        )
                        corrected_tus.append(sen)
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
                and impacted_tus[0].text_unit_type in[TextUnitType.SIN, TextUnitType.PIN]
                and ts.label in (TSLabels.MID, TSLabels.DEL)
            ):
                reduced_in_content = impacted_tus[0].text.replace(ts.text, "", 1)
                impacted_tus = [] if reduced_in_content == "" else [impacted_tus[0].copy_with_text(reduced_in_content)]
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

        # TODO: find a method from detecting sentence splits
        # if tu in post_tus and tu.text not in [t.text for t in prev_tus]:
        #     return SenLabels.SPLIT

        if (
            ts.label in [TSLabels.INS, TSLabels.APP, TSLabels.PAST]
            and tu_starts_within_ts
            and tu_ends_within_ts
        ):
            return SenLabels.NEW

    # TODO: find a method from detecting sentence splits
        # if no_tus_increased is True:
        #     # check if tu without the ts was is prev tus list
        #     # then the status is "split"
        #     ts_split_by_tu = re.split(r"(\.|\?|!)", ts.text)
        #     ts_first_tu = "".join(ts_split_by_tu[:2])
        #     tu_wo_ts = tu.text.replace(ts_first_tu, "")
        #     tu_wo_ts_found_in_prev = False
        #     for i, ptu in enumerate(prev_tus):
        #         if tu_wo_ts in ptu.text:
        #             tu_wo_ts_found_in_prev = True
        #             last_prev_tu = i == len(prev_tus) - 1
        #             break
        #     if tu_wo_ts_found_in_prev and not last_prev_tu:
        #         return SenLabels.SPLIT

        return SenLabels.MOD

    def _assign_tpsf_ids(self, tus: list[TextUnitBuilder], revision_id: int) -> None:
        for tu in tus:
            tu.set_tpsf_id(revision_id)
