from .utils.nlp import check_overlap_with_seq_beginning, calculate_sequence_similarity
import unicodedata


class SentenceClassifier:

    def __init__(self, prev_sens, sens, transforming_sequence):
        self.prev_sens = prev_sens
        self.sens = sens
        self.transforming_sequence = transforming_sequence

        self.delta_current_previous = []
        self.delta_previous_current = []
        self.new_sentences, self.modified_sentences, self.deleted_sentences, self.unchanged_sentences = [], [], [], []

        self.classify_sentence_level_changes()

    def classify_sentence_level_changes(self):
        # if there is no previous TPSF version, all sentences are new sentences
        if not self.prev_sens:
            self.new_sentences = [s for s in self.sens]
            for s in self.new_sentences:
                s.set_label('new')
        # if there is previous TPSF version
        else:
            # sentences which already existed in the previous TPSF:
            self.unchanged_sentences = [sen for sen in self.sens if sen.text in [ps.text for ps in self.prev_sens]]
            for s in self.unchanged_sentences:
                s.set_label('unchanged')
            # sentences which didn't occur in the previous TPSF but do occur in the current TPSF:
            self.delta_current_previous = [sen for sen in self.sens if sen.text not in [ps.text for ps in self.prev_sens]]
            # sentences which occurred in the previous TPSF but don't occur in the current sentences:
            self.delta_previous_current = [s for s in self.prev_sens if s.text not in [cs.text for cs in self.sens]]
            # match sentences from the deltas
            if len(self.delta_current_previous) > 0 or len(self.delta_previous_current) > 0:
                self.compare_deltas()

    def compare_deltas(self):
        if len(self.delta_previous_current) == 0 and len(self.delta_current_previous) > 0:
            affected_text = ' '.join([s.text for s in self.delta_current_previous]).replace('  ', ' ')
            if self.transforming_sequence.text.strip() in affected_text.strip():
                self.new_sentences = self.delta_current_previous
                for s in self.new_sentences:
                    s.set_label('new')
            else:
                print('Warning. The current text version does not contain the transforming sequence (insertion operation).')
        elif len(self.delta_previous_current) > 0 and len(self.delta_current_previous) == 0:
            affected_text = ' '.join([s.text for s in self.delta_previous_current]).replace('  ', ' ')
            if self.transforming_sequence.text.strip() in affected_text.strip():
                self.deleted_sentences = self.delta_previous_current
                for s in self.deleted_sentences:
                    s.set_label('deleted')
            else:
                print('Warning. The previous text version does not contain the transforming sequence (deletion operation).')
        elif len(self.delta_previous_current) == len(self.delta_current_previous) != 0:
            if self.transforming_sequence.label in ['insertion', 'append']:
                normalized_transforming_seq_text = unicodedata.normalize('NFD', self.transforming_sequence.text)
                for cp in self.delta_current_previous:
                    normalized_cp_text = unicodedata.normalize('NFD', cp.text)
                    if normalized_transforming_seq_text.strip() not in normalized_cp_text:
                        overlaps, s1_beginning, index = check_overlap_with_seq_beginning(normalized_transforming_seq_text, normalized_cp_text)
                        normalized_transforming_seq_text = normalized_transforming_seq_text[index:]
                    cp_wo_transforming_seq = cp.text.replace(self.transforming_sequence.text, '')
                    for pc in self.delta_previous_current:
                        if cp_wo_transforming_seq.strip() == pc.text.strip():
                            cp.set_previous_text_version(pc)
                            cp.set_label('modified')
                            self.modified_sentences.append(cp)
                        else:
                            if calculate_sequence_similarity(cp.text, pc.text) > 0.75:
                                cp.set_previous_text_version(pc)
                                cp.set_label('modified')
                                self.modified_sentences.append(cp)
                            else:
                                pc_extended = pc.text + self.transforming_sequence.text
                                if pc_extended.strip() == cp.text.strip():
                                    cp.set_previous_text_version(pc)
                                    cp.set_label('modified')
                                    self.modified_sentences.append(cp)
                                else:
                                    pc_extended = pc.text + ' ' + self.transforming_sequence.text
                                    if pc_extended.strip() == cp.text.strip():
                                        cp.set_previous_text_version(pc)
                                        cp.set_label('modified')
                                        self.modified_sentences.append(cp)
                                    else:
                                        if cp.text not in [s.text for s in self.unchanged_sentences]:
                                            cp.set_label('unchanged')
                                            self.unchanged_sentences.append(cp)
            else:
                for pc in self.delta_previous_current:
                    for cp in self.delta_current_previous:
                        if pc.text.replace(self.transforming_sequence.text.strip(), '').strip() == cp.text.strip():
                            cp.set_previous_text_version(pc)
                            cp.set_label('modified')
                            self.modified_sentences.append(cp)
                        elif pc.text.replace(self.transforming_sequence.text, '').strip() == cp.text.strip():
                            cp.set_previous_text_version(pc)
                            cp.set_label('modified')
                            self.modified_sentences.append(cp)
                        elif calculate_sequence_similarity(pc.text, cp.text) > 0.75:
                            cp.set_previous_text_version(pc)
                            cp.set_label('modified')
                            self.modified_sentences.append(cp)
                        elif pc.text.strip() == self.transforming_sequence.text.strip():
                            cp.set_label('new')
                            self.new_sentences.append(cp)
                        else:
                            cp.set_label('erroneous_automatic_segmentation_detected')
                            self.unchanged_sentences.append(cp)
        else:
            self.process_complex_operations()

    def process_complex_operations(self):
        if len(self.delta_previous_current) != 0 and len(self.delta_current_previous) != 0:
            # If there were less sentences previously than in the current tpsf, this must be an insertion operation.
            # In this case, delta_previous_current must contain only one sentence.
            # It is not possible to perform one insertion that results in two sentences being extended at the same time.
            # Only in case of sentence segmentation error delta_previous_current will be longer than 1 sentence.
            if len(self.delta_previous_current) < len(self.delta_current_previous):
                if len(self.delta_previous_current) > 1:
                    self.verify_segmentation(self.delta_previous_current, self.delta_current_previous)
                else:
                    previous_sentence = self.delta_previous_current[0]
                    previous_sentence_set = False
                    for s in self.delta_current_previous:
                        # If the previous sentence is contained in the current sentence,
                        # the current sentence is a modification of the previous one.
                        if previous_sentence.text.strip('.!?\n') in s.text.strip():
                            s.set_previous_text_version(previous_sentence)
                            s.set_label('modified')
                            self.modified_sentences.append(s)
                        # If the current sentence is contained in the previous sentence,
                        # the current sentence must be a result of a split.
                        elif s.text.strip('.!?\n') in previous_sentence.text.strip():
                            if previous_sentence_set is False:
                                s.set_previous_text_version(previous_sentence)
                                s.set_label('split_result')
                                self.modified_sentences.append(s)
                                previous_sentence_set = True
                            else:
                                s.set_label('split_result')
                                self.new_sentences.append(s)
                        else:
                            s.set_label('new')
                            self.new_sentences.append(s)
            # If there were more sentences previously than now, this must be a deletion operation.
            # In this case, delta_current_previous must contain only one sentence.
            # One deletion may affect two sentences only in case these sentences get merged into one.
            # Only in case of sentence segmentation error delta_current_previous will be longer than 1 sentence.
            elif len(self.delta_previous_current) > len(self.delta_current_previous):
                if len(self.delta_current_previous) > 1:
                    self.verify_segmentation(self.delta_current_previous, self.delta_previous_current)
                else:
                    current_sentence = self.delta_current_previous[0]
                    for s in self.delta_previous_current:
                        # If the current sentence is contained in the previous sentence,
                        # the current sentence is a modification of the previous one.
                        if s.text.strip('.?!') in current_sentence.text.strip():
                            if current_sentence not in self.modified_sentences:
                                current_sentence.set_previous_text_version(s)
                                current_sentence.set_label('merge_result')
                                self.modified_sentences.append(current_sentence)
                            else:
                                s.set_label('deleted_due_to_merge')
                                self.deleted_sentences.append(s)
                        else:
                            s.set_label('deleted_due_to_merge')
                            self.deleted_sentences.append(s)

    def verify_segmentation(self, shorter_list, longer_list):
        for sl in shorter_list:
            for ll in longer_list:
                if ll.text in sl.text:
                    ll.set_label('erroneous_automatic_segmentation_detected')
                    self.unchanged_sentences.append(ll)
                else:
                    new_sen = ll
        new_sen.set_label('new')
        self.new_sentences.append(new_sen)



