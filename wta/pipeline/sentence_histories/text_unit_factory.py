import re
from itertools import zip_longest

import settings
from wta.pipeline.names import SenLabels, TSLabels

from ...utils.nlp import ends_with_end_punctuation, starts_with_uppercase_letter
from ..regularexpressions import RegularExpressions
from .text_unit import Sec, Sen, Sin


class TextUnitFactory:
    def run(self, text, revision_id, ts, prev_tpsf):
        print(
            f"\n\n=============================={revision_id}==============================\n"
        )
        sentence_list = settings.nlp_model.segment_text(text)
        textunit_list = self.split_in_textunits(sentence_list)
        merged_textunit_list = self.merge_double_textunits(textunit_list)
        pre_tus, changed_tus, post_tus = self.detect_tus_diffs(
            merged_textunit_list, ts, prev_tpsf
        )
        print(f"TS: {ts.label.upper()} ({ts.startpos}-{ts.endpos}): |{ts.text}|")
        print(f"TEXT: {text}")
        print(f"INITIAL SENTENCE LIST: {sentence_list}")
        corrected_changed_tus = self.improve_segmentation_with_post_tus(
            changed_tus, post_tus
        )
        tus_states = self.collect_tus_states(
            pre_tus, corrected_changed_tus, post_tus, ts
        )
        corrected_textunits = [*pre_tus, *corrected_changed_tus, *post_tus]
        print(
            f"FINAL TU LIST: {[(type(tu).__name__, tu.state.upper(), tu.text) for tu in corrected_textunits]}"
        )
        return corrected_textunits, tus_states

    def split_in_textunits(self, sentence_list):
        textunit_list = []
        for s in sentence_list:
            contains_only_ws = re.search(RegularExpressions.ONLY_WS_RE, s) is not None
            if contains_only_ws is True:
                sin = Sin(s)
                textunit_list.append(sin)
                continue
            sen_wo_trailing_ws = re.sub(RegularExpressions.TRAILING_WS_RE, "", s)
            if sen_wo_trailing_ws == "»":
                merged_tu_text = (
                    textunit_list[len(textunit_list) - 1].text + sen_wo_trailing_ws
                )
                merged_tu = textunit_list[len(textunit_list) - 1].__class__(
                    merged_tu_text
                )
                textunit_list[len(textunit_list) - 1] = merged_tu
                sin_text = (
                    None
                    if re.search(RegularExpressions.TRAILING_WS_RE, s) is None
                    else re.search(RegularExpressions.TRAILING_WS_RE, s).group(0)
                )
                if sin_text is not None:
                    textunit_list.append(Sin(sin_text))
                continue
            if re.search(RegularExpressions.INITIAL_WS_RE, s) is not None:
                sin = Sin(re.search(RegularExpressions.INITIAL_WS_RE, s).group(0))
                textunit_list.append(sin)
            sen_with_ws_trimmed = re.sub(
                RegularExpressions.INITIAL_WS_RE, "", sen_wo_trailing_ws
            )
            uppercase_letter = starts_with_uppercase_letter(sen_with_ws_trimmed)
            end_punctuation = ends_with_end_punctuation(sen_with_ws_trimmed)
            if not uppercase_letter or not end_punctuation:
                s_wo_init_ws = re.sub(RegularExpressions.INITIAL_WS_RE, "", s)
                sec = Sec(s_wo_init_ws)
                textunit_list.append(sec)
            else:
                sen = Sen(sen_with_ws_trimmed)
                textunit_list.append(sen)
                if re.search(RegularExpressions.TRAILING_WS_RE, s) is not None:
                    sin = Sin(re.search(RegularExpressions.TRAILING_WS_RE, s).group(0))
                    textunit_list.append(sin)
        return textunit_list

    def merge_double_textunits(self, textunit_list):
        doubles = [
            (i, j)
            for i, j in zip_longest(textunit_list, textunit_list[1:])
            if type(i).__name__ == type(j).__name__ != "Sen"
        ]
        if len(doubles) == 0:
            # print(f'No more doubles.')
            return textunit_list
        else:
            # print(f'Detected doubles. Need to merge.')
            prev_merged_text = ""
            merged_textunits = []
            for i, j in zip_longest(textunit_list, textunit_list[1:]):
                if type(i).__name__ == type(j).__name__ != "Sen":
                    merged_tu_text = i.text + j.text
                    text_wo_trailing_ws = re.sub(
                        RegularExpressions.TRAILING_WS_RE, "", merged_tu_text
                    )
                    uppercase_letter = starts_with_uppercase_letter(text_wo_trailing_ws)
                    end_punctuation = ends_with_end_punctuation(text_wo_trailing_ws)
                    if not uppercase_letter or not end_punctuation:
                        merged_tu = i.__class__(merged_tu_text)
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
            return self.merge_double_textunits(merged_textunits)

    def detect_tus_diffs(self, textunits, ts, prev_tpsf):
        if ts.label in [TSLabels.MID, TSLabels.DEL, TSLabels.REPL]:
            pre_tus, changed_tus, post_tus = self.check_what_changed(
                prev_tpsf.textunits, ts
            )
            # if the edit consists in deleting or reducing sentence interspace
            if (
                len(changed_tus) == 1
                and type(changed_tus[0]).__name__ == "Sin"
                and ts.label in [TSLabels.MID, TSLabels.DEL]
            ):
                reduced_sin_content = re.sub(ts.text, "", changed_tus[0].text, count=1)
                if reduced_sin_content == "":
                    changed_tus = []
                elif (
                    re.search(RegularExpressions.ONLY_WS_RE, reduced_sin_content)
                    is not None
                ):
                    sin_content = re.search(
                        RegularExpressions.ONLY_WS_RE, reduced_sin_content
                    ).group(0)
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
            pre_tus, changed_tus, post_tus = self.check_what_changed(textunits, ts)
        return pre_tus, changed_tus, post_tus

    def check_what_changed(self, tus, ts):
        pre_tus = []
        post_tus = []
        changed_tus = []
        currentpos = 0
        for tu in tus:
            startpos, endpos = currentpos, currentpos + len(tu.text) - 1
            if endpos < ts.startpos:
                pre_tus.append(tu)
            elif startpos > ts.endpos:
                post_tus.append(tu)
            else:
                changed_tus.append(tu)
            currentpos = currentpos + len(tu.text)
        return pre_tus, changed_tus, post_tus

    def improve_segmentation_with_post_tus(self, changed_tus, post_tus):
        post_sens = [ptu for ptu in post_tus if type(ptu).__name__ == "Sen"]
        corrected_changed_tus = []
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
                        re.sub(RegularExpressions.TRAILING_WS_RE, "", new_ctu_text)
                    )
                    corrected_changed_tus.append(sen)
                    sin_content = (
                        None
                        if re.search(RegularExpressions.TRAILING_WS_RE, new_ctu_text)
                        is None
                        else re.search(
                            RegularExpressions.TRAILING_WS_RE, new_ctu_text
                        ).group(0)
                    )
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

    def collect_tus_states(self, pre_tus, changed_tus, post_tus, ts):
        tus_states = []
        currentpos = 0
        for tu in [*pre_tus, *changed_tus, *post_tus]:
            if len(tu.text) > 0:
                startpos, endpos = currentpos, currentpos + len(tu.text) - 1
                tu_starts_within_ts = startpos in range(ts.startpos, ts.endpos + 1)
                tu_ends_within_ts = endpos in range(ts.startpos, ts.endpos + 1)
                if tu in pre_tus:
                    tus_states.append(SenLabels.UNC_PRE)
                    tu.set_state(SenLabels.UNC_PRE)
                elif tu in post_tus:
                    tus_states.append(SenLabels.UNC_POST)
                    tu.set_state(SenLabels.UNC_POST)
                else:
                    if (
                        ts.label in [TSLabels.INS, TSLabels.APP, TSLabels.PAST]
                        and tu_starts_within_ts
                        and tu_ends_within_ts
                    ):
                        tus_states.append(SenLabels.NEW)
                        tu.set_state(SenLabels.NEW)
                    else:
                        tus_states.append(SenLabels.MOD)
                        tu.set_state(SenLabels.MOD)
            currentpos = currentpos + len(
                tu.text
            )  # it's the index of the beginning of the next tu
        return tus_states
