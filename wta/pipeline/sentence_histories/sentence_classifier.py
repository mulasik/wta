import unicodedata

import settings
from wta.utils.nlp import (
    calculate_sequence_similarity,
    check_overlap_with_seq_beginning,
)


class SentenceClassifier:
    def __init__(self, prev_sens, sens, ts):
        self.prev_sens = prev_sens
        self.sens = sens
        self.ts = ts
        self.nlp_model = settings.nlp_model
        self.delta_current_previous, self.delta_previous_current = [], []
        (
            self.new_sentences,
            self.modified_sentences,
            self.deleted_sentences,
            self.unchanged_sentences,
            self.transposed_sentences,
        ) = ([], [], [], [], [])
        self.classify_sentence_level_changes()

    def classify_sentence_level_changes(self):
        # if there is no previous TPSF version, all sentences are new sentences
        if not self.prev_sens:
            self.new_sentences = list(self.sens)
            for s in self.new_sentences:
                sen_tagged_tokens = self.nlp_model.tag_words(s.content)
                s.set_tagged_tokens_and_typos(sen_tagged_tokens)
        # if there is previous TPSF version
        else:
            # sentences which already existed in the previous TPSF:
            self.set_unchanged_sentences()
            # sentences which didn't occur in the previous TPSF but do occur in the current TPSF:
            self.delta_current_previous = [
                sen
                for sen in self.sens
                if sen.content not in [ps.content for ps in self.prev_sens]
            ]
            for dcp in self.delta_current_previous:
                sen_tagged_tokens = self.nlp_model.tag_words(dcp.content)
                dcp.set_tagged_tokens_and_typos(sen_tagged_tokens)
            # sentences which occurred in the previous TPSF but don't occur in the current sentences:
            self.delta_previous_current = [
                s
                for s in self.prev_sens
                if s.content not in [cs.content for cs in self.sens]
            ]
            # match sentences from the deltas
            if (
                len(self.delta_current_previous) > 0
                or len(self.delta_previous_current) > 0
            ):
                self.compare_deltas()

    def compare_deltas(self):
        if (
            len(self.delta_previous_current) == 0
            and len(self.delta_current_previous) > 0
        ):
            affected_text = " ".join(
                [s.content for s in self.delta_current_previous]
            ).replace("  ", " ")
            if self.ts.text.strip() in affected_text.strip():
                self.new_sentences = self.delta_current_previous
                for s in self.new_sentences:
                    s.set_label("new")
            else:
                print(
                    "Warning. The current text version does not contain the transforming sequence (insertion operation)."
                )
        elif (
            len(self.delta_previous_current) > 0
            and len(self.delta_current_previous) == 0
        ):
            affected_text = " ".join(
                [s.content for s in self.delta_previous_current]
            ).replace("  ", " ")
            if self.ts.text.strip() in affected_text.strip():
                self.deleted_sentences = self.delta_previous_current
                for s in self.deleted_sentences:
                    s.set_label("deleted")
            else:
                print(
                    "Warning. The previous text version does not contain the transforming sequence (deletion operation)."
                )
        elif len(self.delta_previous_current) == len(self.delta_current_previous) != 0:
            if self.ts.label in ["insertion", "append"]:
                normalized_transforming_seq_text = unicodedata.normalize(
                    "NFD", self.ts.text
                )
                for cp in self.delta_current_previous:
                    normalized_cp_text = unicodedata.normalize("NFD", cp.content)
                    if (
                        normalized_transforming_seq_text.strip()
                        not in normalized_cp_text
                    ):
                        (
                            overlaps,
                            s1_beginning,
                            index,
                        ) = check_overlap_with_seq_beginning(
                            normalized_transforming_seq_text, normalized_cp_text
                        )
                        normalized_transforming_seq_text = (
                            normalized_transforming_seq_text[index:]
                        )
                    cp_wo_transforming_seq = cp.content.replace(self.ts.text, "")
                    for pc in self.delta_previous_current:
                        if cp_wo_transforming_seq.strip() == pc.content.strip() or (
                            calculate_sequence_similarity(cp.content, pc.content) > 0.75
                        ):
                            cp.set_previous_text_version(pc)
                            cp.set_label("modified")
                            self.modified_sentences.append(cp)
                        else:
                            pc_extended = pc.content + self.ts.text
                            if pc_extended.strip() == cp.content.strip():
                                cp.set_previous_text_version(pc)
                                cp.set_label("modified")
                                self.modified_sentences.append(cp)
                            else:
                                pc_extended = pc.content + " " + self.ts.text
                                if pc_extended.strip() == cp.content.strip():
                                    cp.set_previous_text_version(pc)
                                    cp.set_label("modified")
                                    self.modified_sentences.append(cp)
                                else:
                                    if cp.content not in [
                                        s.content for s in self.unchanged_sentences
                                    ]:
                                        cp.set_label("unchanged")
                                        self.unchanged_sentences.append(cp)
            else:
                for pc in self.delta_previous_current:
                    for cp in self.delta_current_previous:
                        if (
                            pc.content.replace(self.ts.text.strip(), "").strip()
                            == cp.content.strip()
                            or pc.content.replace(self.ts.text, "").strip()
                            == cp.content.strip()
                            or calculate_sequence_similarity(pc.content, cp.content)
                            > 0.75
                        ):
                            cp.set_previous_text_version(pc)
                            cp.set_label("modified")
                            self.modified_sentences.append(cp)
                        elif (
                            pc.content.strip() == self.ts.text.strip()
                            and self.ts.label != "pasting"
                        ):
                            cp.set_label("new")
                            self.new_sentences.append(cp)
                        elif (
                            pc.content.strip() == self.ts.text.strip()
                            and self.ts.label == "pasting"
                        ):
                            cp.set_label(
                                "pasted"
                            )  # TODO deal with pasted and transposed
                            self.new_sentences.append(cp)
                        elif (
                            self.ts.label == "pasting"
                            and cp.content.replace(self.ts.text.strip(), "").strip()
                            == pc.content.strip()
                        ):
                            cp.set_label("modified")
                            self.modified_sentences.append(cp)
                        else:
                            cp.set_label("erroneous_automatic_segmentation_detected")
                            self.unchanged_sentences.append(cp)
        else:
            self.process_complex_operations()

    def process_complex_operations(self):
        if (
            len(self.delta_previous_current) != 0
            and len(self.delta_current_previous) != 0
        ):
            # If there were less sentences previously than in the current tpsf, this must be an insertion operation.
            # In this case, delta_previous_current must contain only one sentence.
            # It is not possible to perform one insertion that results in two sentences being extended at the same time.
            # Only in case of sentence segmentation error delta_previous_current will be longer than 1 sentence.
            if len(self.delta_previous_current) < len(self.delta_current_previous):
                if len(self.delta_previous_current) > 1:
                    self.verify_segmentation(
                        self.delta_previous_current, self.delta_current_previous
                    )
                else:
                    previous_sentence = self.delta_previous_current[0]
                    previous_sentence_set = False
                    for s in self.delta_current_previous:
                        # If the previous sentence is contained in the current sentence,
                        # the current sentence is a modification of the previous one.
                        if (
                            previous_sentence.content.strip(".!?\n")
                            in s.content.strip()
                        ):
                            s.set_previous_text_version(previous_sentence)
                            s.set_label("modified")
                            self.modified_sentences.append(s)
                        # If the current sentence is contained in the previous sentence,
                        # the current sentence must be a result of a split.
                        elif (
                            s.content.strip(".!?\n")
                            in previous_sentence.content.strip()
                        ):
                            if previous_sentence_set is False:
                                s.set_previous_text_version(previous_sentence)
                                s.set_label("split_result")
                                self.modified_sentences.append(s)
                                previous_sentence_set = True
                            else:
                                s.set_label("split_result")
                                self.new_sentences.append(s)
                        else:
                            s.set_label("new")
                            self.new_sentences.append(s)
            # If there were more sentences previously than now, this must be a deletion operation.
            # In this case, delta_current_previous must contain only one sentence.
            # One deletion may affect two sentences only in case these sentences get merged into one.
            # Only in case of sentence segmentation error delta_current_previous will be longer than 1 sentence.
            elif len(self.delta_previous_current) > len(self.delta_current_previous):
                if len(self.delta_current_previous) > 1:
                    self.verify_segmentation(
                        self.delta_current_previous, self.delta_previous_current
                    )
                else:
                    current_sentence = self.delta_current_previous[0]
                    for s in self.delta_previous_current:
                        # If the current sentence is contained in the previous sentence,
                        # the current sentence is a modification of the previous one.
                        if s.content.strip(".?!") in current_sentence.content.strip():
                            if current_sentence not in self.modified_sentences:
                                current_sentence.set_previous_text_version(s)
                                current_sentence.set_label("merge_result")
                                self.modified_sentences.append(current_sentence)
                            else:
                                s.set_label("deleted_due_to_merge")
                                self.deleted_sentences.append(s)
                        else:
                            s.set_label("deleted_due_to_merge")
                            self.deleted_sentences.append(s)

    def verify_segmentation(self, shorter_list, longer_list):
        print(
            "\nAttention. A potential sentence segmentation error detected. Verifying segmentation..."
        )
        false_segmentation_candidates = {}
        for sl in shorter_list:
            false_segmentation_candidates[sl] = []
            for ll in longer_list:
                if ll.content in sl.content:
                    false_segmentation_candidates[sl].append(ll)
        for sl_sen, ll_sens in false_segmentation_candidates.items():
            if len(ll_sens) > 0:
                print("Potential incorrect segmentations:")
                for ll_sen in ll_sens:
                    print(f"> {ll_sen}")
                longest_sen_length = max([len(ll_sen.content) for ll_sen in ll_sens])
                for ll_sen in ll_sens:
                    if len(ll_sen.content) == longest_sen_length:
                        prev_sen = ll_sen
                        prev_sen.set_label("modified")
                    else:
                        ll_sen.set_label("erroneous_automatic_segmentation_detected")
                        self.unchanged_sentences.append(ll_sen)
                sl_sen.set_label("modified")
                sl_sen.set_previous_text_version(prev_sen)
                self.modified_sentences.append(sl_sen)
            else:
                print(
                    "Segmentation error not confirmed. The following sentence has been labeled as new:"
                )
                print(f"> {sl_sen}")
                new_sen = sl_sen
                new_sen.set_label("new")
                self.new_sentences.append(new_sen)

    def set_unchanged_sentences(self):
        unchanged_sentences = {
            s.content: [s]
            for s in self.sens
            if s.content in [ps.content for ps in self.prev_sens]
        }
        for ps in self.prev_sens:
            if ps.content in unchanged_sentences.keys():
                unchanged_sentences[ps.content].append(ps)
        for sens in unchanged_sentences.values():
            if sens[0].pos_in_text == sens[1].pos_in_text:
                # print(f'yes: {sens[0].pos_in_text} - {sens[1].pos_in_text}')
                sens[0].set_label("unchanged")
                sens[0].set_tagged_tokens_and_typos(sens[1].tagged_tokens)
                self.unchanged_sentences.append(sens[0])
            else:
                # print(f'no: {sens[0].pos_in_text} - {sens[1].pos_in_text}')
                sens[0].set_label("transposed")
                sens[0].set_tagged_tokens_and_typos(sens[1].tagged_tokens)
                self.transposed_sentences.append(sens[0])
