import itertools
import re
from pathlib import Path
from typing import TYPE_CHECKING

from wta.pipeline import regular_expressions
from wta.pipeline.names import TSLabels, TUState, TUTypes
from wta.pipeline.transformation_layer.ts import TSBuilder
from wta.settings import Settings
from wta.utils.nlp import ends_with_end_punctuation, starts_with_uppercase_letter
from wta.utils.other import ensure_path

from .textunit import TextunitBuilder

if TYPE_CHECKING:
    from wta.pipeline.transformation_layer.tpsf import Tpsf


class TextunitFactory:
    """
    Factory class for generating and managing TextUnitBuilder instances
    based on text revisions and transformation sequences.
    """

    def run(
        self,
        revision_id: int,
        tpsf_text: str,
        tsb: TSBuilder,
        prev_tpsf: "Tpsf | None",
        replaced_text: str,
        ts_text: str,
        settings: Settings,
    ) -> tuple[list[TextunitBuilder], list[TextunitBuilder], list[TextunitBuilder]]:
        """
        Generate a list of text units for the given TPSF.

        Args:
            tpsf_text (str): The text content of the current TPSF (text processing sequence file).
            revision_id (int): Unique identifier for the revision being processed.
            ts (TsBUilder): The transformation sequence representing text changes.
            prev_tpsf (TpsfECM | None): The previous TPSF instance, if available.
            sequence_removed_by_repl (str): Text segment removed in case of a REPL transformation.
            settings (Settings): Configuration and NLP settings for segmentation and processing.

        Returns:
            tuple[list[TextUnitBuilder], list[TextUnitBuilder]]:
                - List of updated/current text units for the current TPSF.
                - List of updated text units from the previous TPSF reflecting transformations.

        Description:
            This method performs the main workflow for TU generation:
            1. Segments the input text into sentences.
            2. Writes the segmented sentences to an output file.
            3. Splits, merges, and adjusts TUs based on transformation rules.
            4. Aligns current and previous TUs, assigning states such as NEW, MOD, DEL, MER, SPLIT, UNC_PRE, UNC_POST.
            5. Assigns TPSF revision IDs to each TU.

        It integrates several internal helper methods for segmentation refinement,
        merging adjacent text units, and handling transformation-specific logic.
    """

        sentence_list = settings.nlp_model.segment_text(tpsf_text)

        _txt_sen_file = settings.config["output_dir"] / "sentence_lists" / settings.filename / f"{revision_id}_sentence_list.txt"
        ensure_path(settings.config["output_dir"] / "sentence_lists" / settings.filename)
        with Path.open(_txt_sen_file, "w") as f:
            str_to_save = ""
            for s in sentence_list:
                str_to_save += f"\n|{s}|\n"
            f.write(str_to_save)

        # if revision_id > 140 and revision_id < 151:
            # print(f"\n\n==========================================={revision_id}===========================================\n")
            # print("Extracting text units...")
        # after_end_pos = -1 if tsb.endpos is None else tsb.endpos + 1
        # if tsb.label in [TSLabels.DEL, TSLabels.MID] and prev_tpsf:
        #     print(f"Text segment from previous TPSF impacted by the TS: |{prev_tpsf.text[tsb.startpos:after_end_pos]}|\n")
        # elif tsb.label == TSLabels.REPL and prev_tpsf and tsb.startpos and tsb.rplcmt_textlen:
        #     print(f"Text segment from previous TPSF impacted by the TS: |{prev_tpsf.text[tsb.startpos:tsb.startpos+tsb.rplcmt_textlen]}|\n")
#         print(f"""
# >> INITIAL TRANSFORMING SEQUENCE DETAILS <<
# TS: {tsb.label.upper()} ({tsb.startpos}-{tsb.endpos})
# |{ts_text}|
# TS preceding pause: {tsb.pauses[0] if len(tsb.pauses)>0 else None}
# TS following pause: {tsb.following_pause}
# TS pauses: {tsb.pauses}
# """)

        # print(f">>> INITIAL SENTENCE LIST: {sentence_list}\n")
        textunit_list = self._split_in_textunits(sentence_list)
        merged_textunit_list = self._merge_double_textunits(textunit_list)
        # if revision_id > 140 and revision_id < 151:
        #     print(f">>> INITIAL TEXTUNITS: {[str(tu) for tu in textunit_list]}\n")
        #     print(f">>> TUs AFTER 1st MERGING STEP: {[str(tu) for tu in merged_textunit_list]}\n")
        corrected_tus = self._improve_segmentation_with_prev_tus(merged_textunit_list, prev_tpsf, revision_id)
        # if revision_id > 140 and revision_id < 151:
        #     print( f">>> CORRECTED TUs: {[str(tu) for tu in corrected_tus]}\n")
        extended_textunit_list = self._retrieve_tu_positions(corrected_tus)
        textunit_list, _ = self._retrieve_tu_states(extended_textunit_list, tsb, prev_tpsf, replaced_text, ts_text)
        # print(f">>> ALL TUs: {[str(tu) for tu in textunit_list]}\n")
        merged_modsensens_textunits_list = self._merge_modsec_and_modsen(textunit_list)
        # print(f">>> TUs AFTER SECOND MERGING STEP: {[str(tu) for tu in merged_modsensens_textunits_list]}\n")
        remerged_textunit_list = self._merge_double_textunits(merged_modsensens_textunits_list)
        # print(f">>> TUs AFTER 2nd MERGING STEP: {[str(tu) for tu in remerged_textunit_list]}\n")
        updated_textunit_list, updated_prev_textunit_list = self._retrieve_tu_states(remerged_textunit_list, tsb, prev_tpsf, replaced_text, ts_text)
        # print(f">>> PREV TUs (1): {[str(tu) for tu in updated_prev_textunit_list]}\n")
        extended_textunit_list = self._retrieve_tu_positions(updated_textunit_list)
        # print(f"\n>>> *IMPACTED* TUs AFTER 3rd MERGING STEP: {[str(tu) for tu in extended_textunit_list if tu.state not in [TUState.UNC_PRE,TUState.UNC_POST]]}\n")
        updated_textunit_list, updated_prev_textunit_list = self._detect_merges_and_splits(extended_textunit_list, updated_prev_textunit_list, tsb, tpsf_text)
        self._assign_tpsf_ids(updated_textunit_list, revision_id)
        # if revision_id > 140 and revision_id < 151:
        #     print(f">>> FINAL TU LIST: {[str(tu) for tu in updated_textunit_list]}\n")
        # print(f">>> PREVIOUS *IMPACTED* TUs: {[str(tu) for tu in updated_prev_textunit_list if tu.state not in [TUState.UNC_PRE,TUState.UNC_POST]]}\n")
        # for tu in updated_textunit_list:
        #         if tu.state in [TUState.UNC_PRE, TUState.UNC_POST]:
        #             tu.set_segment(None)
        deleted_textunits = [ptu for ptu in updated_prev_textunit_list if ptu.state == TUState.DEL]
        # print(f">>> DELETED TUs: {[str(tu) for tu in deleted_textunits if tu.state == TUState.DEL]}\n")

        return updated_textunit_list, updated_prev_textunit_list, deleted_textunits

    def _collect_preceding_sins_and_pins(
        self, seq: str, textunit_list: list[TextunitBuilder]
    ) -> tuple[str, list[TextunitBuilder]]:
        starts_with_s = regular_expressions.PRECEDING_S_RE.search(seq)
        starts_with_pws = regular_expressions.PRECEDING_PWS_RE.search(seq)
        if starts_with_s is not None:
            sin_content = starts_with_s.group(0)
            sin = TextunitBuilder(TUTypes.SIN, sin_content)
            textunit_list.append(sin)
            seq = re.sub(sin_content, "", seq)
        elif starts_with_pws is not None:
            pin_content = starts_with_pws.group(0)
            pin = TextunitBuilder(TUTypes.PIN, pin_content)
            textunit_list.append(pin)
            seq = re.sub(pin_content, "", seq)
        else:
            return seq, textunit_list
        return self._collect_preceding_sins_and_pins(seq, textunit_list)

    def _find_middle_pins(self, seq: str) -> list[str]:
        middle_pins = regular_expressions.MIDDLE_PWS_RE.findall(seq)
        middle_pin_matches = []
        for middle_pin_tup in middle_pins:
            match = next(t for t in middle_pin_tup if t != "")
            middle_pin_matches.append(match)
        return middle_pin_matches

    def _split_tu_by_pins(
        self, seq: str, textunit_list: list[TextunitBuilder], middle_pins: list[str]
    ) -> tuple[str, list[TextunitBuilder]]:
        if middle_pins == []:
            return seq, textunit_list
        middle_pin = middle_pins.pop(0)
        # print(f"Splitting by the PIN: |{middle_pin}|")
        split_tus = seq.split(middle_pin, 1)
        # print(f"There are {len(split_tus)} TUs in this sequence split by middle PIN:")
        first_tu = split_tus[0]
        second_tu = "" if len(split_tus) == 1 else split_tus[1]
        # print(f"First TU: |{first_tu}|")
        # print(f"Second TU: |{second_tu}|")
        _, textunit_list = self._retrieve_sen_or_sec(first_tu, textunit_list)
        pin = TextunitBuilder(TUTypes.PIN, middle_pin)
        textunit_list.append(pin)
        return self._split_tu_by_pins(second_tu, textunit_list, middle_pins)

    def _trim_trailing_sins_and_pins(self, seq: str) -> str:
        ends_with_s = regular_expressions.TRAILING_S_RE.search(seq)
        ends_with_pws = regular_expressions.TRAILING_PWS_RE.search(seq)
        if ends_with_s is not None:
            seq = re.sub(regular_expressions.TRAILING_S_RE, "", seq)
        elif ends_with_pws is not None:
            seq = re.sub(regular_expressions.TRAILING_PWS_RE, "", seq)
        else:
            return seq
        return self._trim_trailing_sins_and_pins(seq)

    def _collect_trailing_sins_and_pins(
        self, seq: str, textunit_list: list[TextunitBuilder]
    ) -> tuple[str, list[TextunitBuilder]]:
        ends_with_s = regular_expressions.TRAILING_S_RE.search(seq)
        ends_with_pws = regular_expressions.TRAILING_PWS_RE.search(seq)
        if ends_with_s is not None:
            sin_content = ends_with_s.group(0)
            sin = TextunitBuilder(TUTypes.SIN, sin_content)
            textunit_list.append(sin)
            seq = re.sub(sin_content, "", seq)
        elif ends_with_pws is not None:
            pin_content = ends_with_pws.group(0)
            pin = TextunitBuilder(TUTypes.PIN, pin_content)
            textunit_list.append(pin)
            seq = re.sub(pin_content, "", seq)
        else:
            # seq should be empty after the function is executed
            return seq, textunit_list
        return self._collect_trailing_sins_and_pins(seq, textunit_list)

    def _retrieve_sen_or_sec(
        self, seq: str, textunit_list: list[TextunitBuilder]
    ) -> tuple[str, list[TextunitBuilder]]:
        # if the seq contains only space characters, no SEN or SEC can be retrieved
        if re.search(regular_expressions.ONLY_S_RE, seq) is not None:
            return seq, textunit_list
        seq_with_whitespaces_trimmed = self._trim_trailing_sins_and_pins(seq)
        uppercase_letter = starts_with_uppercase_letter(seq_with_whitespaces_trimmed)
        end_punctuation = ends_with_end_punctuation(seq_with_whitespaces_trimmed)
        if (
            (not uppercase_letter
            or not end_punctuation)
            and re.search(regular_expressions.ONLY_S_RE, seq) is None
        ):
            sec = TextunitBuilder(TUTypes.SEC, seq)
            textunit_list.append(sec)
            seq = ""
        else:
            sen = TextunitBuilder(TUTypes.SEN, seq_with_whitespaces_trimmed)
            textunit_list.append(sen)
            seq = re.sub(seq_with_whitespaces_trimmed, "", seq)
            seq, textunit_list = self._collect_trailing_sins_and_pins(seq, textunit_list)
        # seq should be empty after the function is executed
        return seq, textunit_list

    def _split_in_textunits(self, sentence_list: list[str]) -> list[TextunitBuilder]:
        textunit_list: list[TextunitBuilder] = []

        for s in sentence_list:
            # check if s contains only space chars > SIN
            contains_only_s = regular_expressions.ONLY_S_RE.search(s)
            if contains_only_s is not None:
                sin = TextunitBuilder(TUTypes.SIN, s)
                textunit_list.append(sin)
                continue
            # check if s contains only paragraph whitespace chars > PIN
            contains_only_pws = regular_expressions.ONLY_PWS_RE.search(s)
            if contains_only_pws is not None:
                pin = TextunitBuilder(TUTypes.PIN, s)
                textunit_list.append(pin)
                continue
            # Handling special cases: incorrect SpaCy segmentation in case of citations with «»
            # sentence returned by SpaCy starts with end citation mark (which should be part of the previous sentence)
            found_end_citation_at_beginning = re.search(r"\A»", s)
            if found_end_citation_at_beginning is not None:
                textunit_list[-1] = textunit_list[-1].copy_with_appended_text("»")
                s = re.sub(regular_expressions.PRECEDING_END_CITATION, "", s)
            found_question_mark_at_beginning = re.search(r"\A\?+", s)
            if found_question_mark_at_beginning is not None:
                found_char = found_question_mark_at_beginning.group()
                textunit_list[-1] = textunit_list[-1].copy_with_appended_text(found_char)
                s = re.sub(re.escape(found_char), "", s)
            seq, textunit_list = self._collect_preceding_sins_and_pins(s, textunit_list)
            middle_pins = self._find_middle_pins(seq)
            seq, textunit_list = self._split_tu_by_pins(seq, textunit_list, middle_pins)
            if seq != "":
                seq, textunit_list = self._retrieve_sen_or_sec(seq, textunit_list)
            if s != "":
                seq, textunit_list = self._collect_trailing_sins_and_pins(seq, textunit_list)
        return textunit_list

    def _merge_double_textunits(
        self, textunit_list: list[TextunitBuilder]
    ) -> list[TextunitBuilder]:
        if not any(
            i.type == j.type != TUTypes.SEN
            for (i, j) in itertools.pairwise(textunit_list)
        ):
            # print(f'No more doubles.')
            return textunit_list

        # print(f'Detected doubles. Need to merge.')
        prev_merged_text = ""
        merged_textunits = []
        for i, j in itertools.pairwise(textunit_list):
            if (
                i.type == j.type != TUTypes.SEN
                and i.text != prev_merged_text
            ):
                merged_tu_text = i.text + j.text
                text_wo_trailing_ws = self._trim_trailing_sins_and_pins(merged_tu_text)
                uppercase_letter = starts_with_uppercase_letter(text_wo_trailing_ws)
                end_punctuation = ends_with_end_punctuation(text_wo_trailing_ws)
                if not uppercase_letter or not end_punctuation:
                    merged_tu = i.copy_with_text(merged_tu_text)
                    merged_textunits.append(merged_tu)
                else:
                    sen = TextunitBuilder(TUTypes.SEN, text_wo_trailing_ws)
                    merged_textunits.append(sen)
                    remaining_content = merged_tu_text.replace(text_wo_trailing_ws, "")
                    _, merged_textunits = self._collect_trailing_sins_and_pins(
                        remaining_content, merged_textunits
                    )
                prev_merged_text = j.text
            elif i.text != prev_merged_text:
                merged_textunits.append(i)
                prev_merged_text = ""
        if j.text != prev_merged_text:
            merged_textunits.append(j)
        return self._merge_double_textunits(merged_textunits)

    # if a modified SEC is followed by a modified SEN
    def _merge_modsec_and_modsen(
            self, textunit_list: list[TextunitBuilder]
    ) -> list[TextunitBuilder]:
        prev_merged_text = ""
        merged_textunits = []
        for i, j in itertools.pairwise(textunit_list):
            # print("\n****************")
            # print(i.text_unit_type, i.state, i.text)
            # print(j.text_unit_type, j.state, j.text)
            if (
                i.type == TUTypes.SEC and j.type == TUTypes.SEN
                and i.state == j.state == TUState.MOD
                and i.text != prev_merged_text
            ):
                print("INFO: encountered a modified SEC followed by a modified SEN without an interspace inbetween. "
                      "\nThe modified SEC:"
                      f"\n|{i.text}|"
                      "\nThe subsequent modified SEN:"
                      f"\n|{j.text}|"
                      "\nThis case is not allowed according to definitions and constraints implemented in THEtool. "
                      "\nMerging the two text units into one modified text unit.")
                merged_tu_text = i.text + j.text
                text_wo_trailing_ws = self._trim_trailing_sins_and_pins(merged_tu_text)
                uppercase_letter = starts_with_uppercase_letter(text_wo_trailing_ws)
                end_punctuation = ends_with_end_punctuation(text_wo_trailing_ws)
                if not uppercase_letter or not end_punctuation:
                    merged_tu = i.copy_with_text(merged_tu_text)
                    merged_tu.set_state(TUState.MOD)
                    merged_tu.set_tpsf_id(i.tpsf_id if i.tpsf_id is not None else -1)
                    merged_textunits.append(merged_tu)
                else:
                    merged_tu = TextunitBuilder(TUTypes.SEN, text_wo_trailing_ws)
                    merged_tu.set_state(TUState.MOD)
                    merged_tu.set_tpsf_id(i.tpsf_id if i.tpsf_id is not None else -1)
                    merged_textunits.append(merged_tu)
                    remaining_content = merged_tu_text.replace(text_wo_trailing_ws, "")
                    _, merged_textunits = self._collect_trailing_sins_and_pins(
                        remaining_content, merged_textunits
                    )
                prev_merged_text = j.text
                print(f"UPDATE: Merged the two text units into one {merged_tu.state} {'SEC' if merged_tu.type == TUTypes.SEC else 'SEN'}:"
                f"\n|{merged_tu.text}|")
                # print(f"Prev merged text is |{prev_merged_text}|")
            elif i.text != prev_merged_text:
                # print(f"Will add the TU |{i.text}| as it is different than |{prev_merged_text}|")
                merged_textunits.append(i)
        if len(textunit_list) > 0 and textunit_list[-1].text != prev_merged_text:
            # print(f"And will add the TU |{textunit_list[-1].text}| as it is different than |{prev_merged_text}|")
            merged_textunits.append(textunit_list[-1])
        return merged_textunits

    def _improve_segmentation_with_prev_tus(
        self, tus: list[TextunitBuilder], prev_tpsf: "Tpsf | None", revision_id: int
    ) -> list[TextunitBuilder]:
        """
            SEN definition:
            Once a sequence of characters has been identified as a sentence, its status remains
            unchanged as long as the writer does not clearly signal a revision of the sentence scope
            by removing the capitalisation of the initial letter or adjusting the final punctuation mark.
            In other words, as long as the sentence frame stays untouched, we treat the sequence
            of characters within this frame as a sentence, even if other sentencehood criteria are not
            satisfied
        """
        prev_sens = (
            []
            if prev_tpsf is None
            else [
                ptu.copy_to_builder()
                for ptu in prev_tpsf.tus
                if ptu.type == TUTypes.SEN
            ]
        )
        corrected_tus: list[TextunitBuilder] = []

        tus_contained_in_prev_sens: dict[str, list[TextunitBuilder]] = {}

        if prev_tpsf is not None:
            # print(f"Prev SENs: {[s.text for s in prev_sens]}")
            for ptu in prev_tpsf.tus:
                for tu in tus:
                    if tu.type in [TUTypes.SEC, TUTypes.SEN]:
                        matching_tu_index = ptu.text.find(tu.text) # if tu.text_unit_type in [TUTypes.SEC, TUTypes.SEN] else None
                        if matching_tu_index != -1 and ptu.text not in tus_contained_in_prev_sens:
                            tus_contained_in_prev_sens.update({ptu.text: [tu]})
                        elif matching_tu_index != -1 and ptu.text in tus_contained_in_prev_sens:
                            tus_contained_in_prev_sens[ptu.text].append(tu)
                # if ptu.text in tus_contained_in_prev_sens:
                #     print(ptu.text == "".join([tu.text for tu in tus_contained_in_prev_sens[ptu.text]]))
                #     print(f"These are the tus contained in previous SENs: {[(tu.text, tu.text_unit_type) for tu in tus_contained_in_prev_sens[ptu.text]]}")

        for tu in tus:
            matching_prev_sens = [
                psen for psen in prev_sens if psen.text in tu.text
            ]  # is any previous sentence part of the text unit?
            # print(f"Matching prev SENs are: {[s.text for s in matching_prev_sens]}")
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
                            sec = TextunitBuilder(TUTypes.SEC, new_ctu_text)
                            corrected_tus.append(sec)
                        else:
                            sen = TextunitBuilder(
                                TUTypes.SEN,
                                regular_expressions.TRAILING_S_RE.sub("", new_ctu_text),
                            )
                            corrected_tus.append(sen)
                elif matching_sen_index > 0 and matching_sen_index + len(matching_sen.text) == len(tu.text):
                    new_ctu_text = tu.text.replace(matching_sen.text, "")
                    sin = None
                    if len(new_ctu_text) > 1 and new_ctu_text[-1] == " " and new_ctu_text[-2] == ".":
                        # print("It is not a SEC but a SEN and a SIN.")
                        new_ctu_text_to_split = new_ctu_text
                        new_ctu_text = new_ctu_text_to_split[:-1]
                        new_sin_text = new_ctu_text_to_split[-1]
                        sin = TextunitBuilder(TUTypes.SIN, new_sin_text)
                    if new_ctu_text != "":
                        uppercase_letter = starts_with_uppercase_letter(new_ctu_text)
                        end_punctuation = ends_with_end_punctuation(new_ctu_text)
                        if not uppercase_letter or not end_punctuation:
                            sec = TextunitBuilder(TUTypes.SEC, new_ctu_text)
                            corrected_tus.append(sec)
                        else:
                            sen = TextunitBuilder(
                                TUTypes.SEN,
                                regular_expressions.TRAILING_S_RE.sub("", new_ctu_text),
                            )
                            corrected_tus.append(sen)
                        if sin is not None:
                            corrected_tus.append(sin)
                    corrected_tus.append(matching_sen)
                else:
                    corrected_tus.append(tu)
            # if no previous complete sentence (SEN) is contained in the text unit
            elif len(matching_prev_sens) == 0:
                corrected_tus.append(tu)
            # if there is more than 1 previous complete sentence contained in the text unit
            else:
                print(
                    f"WARNING for TPSF {revision_id}: {len(matching_prev_sens)} sentences have been found within the textunit {tu.text}. "
                )
        return corrected_tus

    def _retrieve_tu_positions(
            self,
            textunits: list[TextunitBuilder]
    ) -> list[TextunitBuilder]:
        currentpos = 0
        for tu in textunits:
            startpos, endpos = currentpos, currentpos + len(tu.text) - 1
            tu.set_startpos(startpos)
            tu.set_endpos(endpos)
            currentpos = currentpos + len(tu.text)
        return textunits

    def _retrieve_tu_states(
            self,
            textunits: list[TextunitBuilder],
            tsb: TSBuilder,
            prev_tpsf: "Tpsf | None",
            replaced_text: str,
            ts_text: str
    ) -> tuple[list[TextunitBuilder], list[TextunitBuilder]]:

        prev_textunits: list[TextunitBuilder] = (
            []
            if prev_tpsf is None
            else [tu.copy_to_builder() for tu in prev_tpsf.tus]
        )
        pre_tus = []
        post_tus = []
        if tsb.label in [TSLabels.MID, TSLabels.DEL]:
            # print(">>>>> Checking which TUs are impacted by deleting operations...")
            for ptu in prev_textunits:
                # print(f"Text unit: |{ptu}|")
                # print(f"TU position: {ptu.startpos, ptu.endpos}")
                # print(f"TS position: {tsb.startpos, tsb.endpos}")
                # if the tu occurs before the TS
                if (
                    ptu.endpos is not None and ptu.endpos < tsb.startpos
                ):
                    pre_tus.append(ptu)
                    ptu.set_state(TUState.UNC_PRE)
                # if the tu occurs after the TS
                elif (
                    tsb.endpos is not None
                    and ptu.startpos is not None
                    and ptu.startpos > tsb.endpos
                ):
                    post_tus.append(ptu)
                    ptu.set_state(TUState.UNC_POST)
                # if tu is included in the TS
                elif ptu.text.strip() in ts_text.strip():
                    ptu.set_state(TUState.DEL)
                else:
                    ptu.set_state(TUState.MOD)
            # update states and positions of current textunits
            currentpos = 0
            for tu in textunits:
                # print(f"Text unit: |{tu}|")
                # print(f"TU position: {tu.startpos, tu.endpos}")
                # print(f"TS position: {tsb.startpos, tsb.endpos}")
                # if the tu occurs before the TS
                if (
                    tu.endpos is not None
                    and tu.endpos <= tsb.startpos
                    and tu.text in [ptu.text for ptu in pre_tus]
                    ):
                    pre_tus.append(tu)
                    tu.set_state(TUState.UNC_PRE)
                # if the tu occurs after the TS
                elif (
                    tsb.endpos is not None
                    and tu.startpos is not None
                    and tu.startpos+len(ts_text) > tsb.endpos
                    and tu.text in [ptu.text for ptu in post_tus]
                ):
                    post_tus.append(tu)
                    tu.set_state(TUState.UNC_POST)
                # if tu is included in the TS
                elif tu.text.strip() in ts_text.strip():
                    tu.set_state(TUState.NEW)
                else:
                    tu.set_state(TUState.MOD)
                currentpos = currentpos + len(tu.text)

        elif tsb.label in [TSLabels.APP, TSLabels.INS, TSLabels.PAST, TSLabels.REPL]:
            # print(">>>>> Checking which TUs are impacted by producing/replacing operations...")
            currentpos = 0
            for tu in textunits:
                # print(f"Text unit: |{tu}|")
                # print(f"TU position: {tu.startpos, tu.endpos}")
                # print(f"TS position: {tsb.startpos, tsb.endpos}")
                # if the tu occurs before the TS
                if (
                    tu.endpos is not None
                    and tu.endpos < tsb.startpos
                    ):
                    pre_tus.append(tu)
                    tu.set_state(TUState.UNC_PRE)
                # if the tu occurs after the TS
                elif (
                    tsb.endpos is not None
                    and tu.startpos is not None
                    and tu.startpos > tsb.endpos
                ):
                    post_tus.append(tu)
                    tu.set_state(TUState.UNC_POST)
                # if tu is included in the TS
                elif tu.text.strip() in ts_text.strip():
                    tu.set_state(TUState.NEW)
                else:
                    tu.set_state(TUState.MOD)
                currentpos = currentpos + len(tu.text)
                # print(f"TU after state assignment: |{tu.state}|")
        else:
            print(f"Encountered an unknown TS label: {tsb.label}")

        if tsb.label == TSLabels.REPL:
            # update states of prev textunits after replacement
            for ptu in prev_textunits:
                # print(f"Text unit: |{ptu}|")
                # print(f"TU position: {ptu.startpos, ptu.endpos}")
                # print(f"TS position: {tsb.startpos, tsb.endpos}")
                # if the tu occurs before the TS
                if (ptu.endpos is not None
                    and ptu.endpos <= tsb.startpos
                    and ptu.text in [ptu.text for ptu in pre_tus]
                    ):
                    ptu.set_state(TUState.UNC_PRE)
                # if the tu occurs after the TS

                elif (
                    tsb.endpos is not None
                    and ptu.startpos is not None
                    and ptu.startpos > tsb.endpos
                    and ptu.text in [ptu.text for ptu in post_tus]
                ):
                    ptu.set_state(TUState.UNC_POST)
                # if tu is included in the TS

                elif replaced_text is not None and ptu.text.strip() in replaced_text:
                    ptu.set_state(TUState.DEL)

                else:
                    ptu.set_state(TUState.MOD)

        return textunits, prev_textunits

    def _detect_merges_and_splits(
            self,
            textunit_list: list[TextunitBuilder],
            prev_textunit_list: list[TextunitBuilder],
            tsb: TSBuilder,
            text: str
            ) -> tuple[list[TextunitBuilder], list[TextunitBuilder]]:
        modified_spsfs = [tu for tu in textunit_list if tu.state in [TUState.MOD] and tu.type in [TUTypes.SEC, TUTypes.SEN]]
        modified_prev_spsfs = [tu for tu in prev_textunit_list if tu.state in [TUState.MOD] and tu.type in [TUTypes.SEC, TUTypes.SEN]]
        new_spsfs = [tu for tu in textunit_list if tu.state in [TUState.NEW] and tu.type in [TUTypes.SEC, TUTypes.SEN]]
        # probably sentence merge:
        if len(modified_spsfs) == 1 and len(modified_prev_spsfs) == 2:
            for pspsf in modified_prev_spsfs:
                # if previous SPSF found in the current impacted SPSFs, change the state of the current SPSF to "merged"
                # and the state of the previous SPSF to "unchanged"
                if pspsf.text in modified_spsfs[0].text:
                    modified_spsfs[0].set_state(TUState.MER)
                    pspsf.set_state(TUState.MER)
                # if previous SPSF not found in the current impacted SPSFs, change the state of the previous SPSF to "merged"
                else:
                    pspsf.set_state(TUState.MER)
        # probably sentence split:
        if len(modified_spsfs) == 2 and len(modified_prev_spsfs) == 1 and len(new_spsfs) == 0:
            modified_tus = [tu for tu in textunit_list if tu.state in [TUState.MOD, TUState.NEW]]
            startpos = tsb.startpos
            for i, mtu in enumerate(modified_tus):
                if mtu.endpos is not None and tsb.endpos is not None:
                    endpos = mtu.endpos if i != len(modified_tus)-1 else tsb.endpos
                    segment = text[startpos:endpos+1]
                    if segment in mtu.text:
                        mtu.set_state(TUState.SPLIT)
                    startpos = mtu.endpos + 1
            modified_prev_spsfs[0].set_state(TUState.SPLIT)
        return textunit_list, prev_textunit_list

    def _assign_tpsf_ids(self, tus: list[TextunitBuilder], revision_id: int) -> None:
        for tu in tus:
            tu.set_tpsf_id(revision_id)

    def _extract_startpost_and_endpos(self, tus: list[TextunitBuilder]) -> None:
        startpos = 0
        for tu in tus:
            endpos = startpos + len(tu.text)-1
            tu.set_startpos(startpos)
            tu.set_endpos(endpos)
            startpos = endpos+1
