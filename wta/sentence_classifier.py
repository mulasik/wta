import re


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
            # sentences which didn't occur in the previous TPSF but do occur in the current TPSF:
            self.delta_current_previous = [sen for sen in self.sens if sen.text not in [ps.text for ps in self.prev_sens]]
            # sentences which occurred in the previous TPSF but don't occur in the current sentences:
            self.delta_previous_current = [s for s in self.prev_sens if s.text not in [cs.text for cs in self.sens]]
            # match sentences from the deltas
            if len(self.delta_current_previous) > 0 or len(self.delta_previous_current) > 0:
                self.compare_deltas()
            # sentences which already existed in the previous TPSF:
            self.unchanged_sentences = [sen for sen in self.sens if sen.text in [ps.text for ps in self.prev_sens]]
            for s in self.unchanged_sentences:
                s.set_label('unchanged')

    def compare_deltas(self):
        if len(self.delta_previous_current) == 0 and len(self.delta_current_previous) > 0:
            self.new_sentences = self.delta_current_previous
            for s in self.new_sentences:
                s.set_label('new')
        elif len(self.delta_previous_current) > 0 and len(self.delta_current_previous) == 0:
            self.deleted_sentences = self.delta_previous_current
            for s in self.deleted_sentences:
                s.set_label('deleted')
        elif len(self.delta_previous_current) == len(self.delta_current_previous) != 0:
            for pc, cp in zip(self.delta_previous_current, self.delta_current_previous):
                cp.set_previous_text_version(pc)
                cp.set_label('modified')
                self.modified_sentences.append(cp)
        else:
            self.process_complex_operations()

    def process_complex_operations(self):
        if len(self.delta_previous_current) != 0 and len(self.delta_current_previous) != 0:
            # If there were less sentences previously than in the current tpsf, this must be an insertion operation.
            # In this case, delta_previous_current must contain only one sentence.
            # It is not possible to perform one insertion that results in two sentences being extended at the same time.
            if len(self.delta_previous_current) < len(self.delta_current_previous):
                previous_sentence = self.delta_previous_current[0]
                previous_sentence_set = False
                for s in self.delta_current_previous:
                    # If the previous sentence is contained in the current sentence,
                    # the current sentence is a modification of the previous one.
                    if previous_sentence.text.strip() in s.text.strip():
                        s.set_previous_text_version(previous_sentence)
                        s.set_label('modified')
                        self.modified_sentences.append(s)
                    # If the current sentence is contained in the previous sentence,
                    # the current sentence must be a result of a split.
                    elif s.text.strip('.!?') in previous_sentence.text.strip():
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
            elif len(self.delta_previous_current) > len(self.delta_current_previous):
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

