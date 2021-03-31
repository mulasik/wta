import uuid
from .sentence import Sentence
from .utils.nlp import retrieve_match_range


class SentenceHistoryGenerator:

    def __init__(self, tpsfs):
        self.tpsfs = tpsfs
        self.sentence_history = {}
        self.generate_sentence_history()
        self.filtered_sentence_history = {}
        self.filter_sentence_history()

    def generate_sentence_history(self):
        global_new_sens = []
        for tpsf in self.tpsfs:
            revision_relevance = tpsf.morphosyntactic_relevance
            new_sens = tpsf.new_sentences
            modified_sens = tpsf.modified_sentences
            del_sens = tpsf.deleted_sentences
            unchanged_sens = tpsf.unchanged_sentences
            for ns in new_sens:
                global_new_sens_texts = [ns.text for ns in global_new_sens]
                if ns.text in global_new_sens_texts:
                    ns.set_label('reinserted')
                    for id, sens in self.sentence_history.items():
                        texts = [s.text for s in sens]
                        if ns.text in texts:
                            existing_id = id
                            ns.set_revision_morphosyntactic_relevance(revision_relevance)
                            self.sentence_history[existing_id].append(ns)
                else:
                    uid = uuid.uuid1().int
                    ns.set_revision_morphosyntactic_relevance(revision_relevance)
                    self.sentence_history[uid] = [ns]
                global_new_sens.append(ns)
            for es in modified_sens:
                es.set_revision_morphosyntactic_relevance(revision_relevance)
                for id, sens in self.sentence_history.items():
                    sens_texts = [sen.text for sen in sens]
                    if es.previous_sentence.text in sens_texts:
                        self.sentence_history[id].append(es)
            for ds in del_sens:
                for id, sens in self.sentence_history.items():
                    sens_texts = [sen.text for sen in sens]
                    if ds.text in sens_texts:
                        if ds.label == 'deleted_due_to_merge':
                            label = 'deleted_due_to_merge'
                        else:
                            label = 'deleted'
                        sentence_remains = Sentence(None, None, None, ds.revision_id, None, None)
                        sentence_remains.set_label(label)
                        sentence_remains.set_revision_morphosyntactic_relevance(revision_relevance)
                        self.sentence_history[id].append(sentence_remains)
            for us in unchanged_sens:
                us.set_revision_morphosyntactic_relevance(revision_relevance)
                for id, sens in self.sentence_history.items():
                    sens_texts = [sen.text for sen in sens]
                    if us.text in sens_texts:
                        self.sentence_history[id].append(us)

    def filter_sentence_history(self):
        for id, sen_versions in self.sentence_history.items():
            self.filtered_sentence_history[id] = []
            prev_sv = None
            for senid, sv in enumerate(sen_versions):
                if prev_sv is None and len(sen_versions) > 1:
                    prev_sv = sv
                elif prev_sv is None and sv is not None and len(sen_versions) == 1:
                    self.filtered_sentence_history[id].append(sv)
                elif sv.text is None and len(sen_versions) == 1:
                    continue
                elif sv.text is None and prev_sv is not None and len(sen_versions) > 1:
                    self.filtered_sentence_history[id].append(sv)
                elif sv.text is not None and prev_sv is not None and len(sen_versions) > 1:
                    if sv is None:
                        self.filtered_sentence_history[id].append(sv)
                    else:
                        match_ranges = retrieve_match_range(prev_sv.text, sv.text)
                        match = 0
                        for mr in match_ranges:
                            # a small match range may refer to one letter
                            # which may occur at many positions hence it's ignored
                            if mr.size > 1:
                                match += mr.size
                        prev_sen_len = len(prev_sv.text)
                        sen_len = len(sv.text)
                        mismatch = prev_sen_len - match
                        if mismatch > 3:
                            self.filtered_sentence_history[id].append(prev_sv)
                        elif mismatch == 0 and len(match_ranges) > 2 and sen_len - match > 3:
                            self.filtered_sentence_history[id].append(prev_sv)
                        if senid + 1 == len(sen_versions) and sv not in self.filtered_sentence_history[id]:
                            self.filtered_sentence_history[id].append(sv)
                    prev_sv = sv
                if len(sen_versions) == 1 and sv not in self.filtered_sentence_history[id]:
                    self.filtered_sentence_history[id].append(sv)

