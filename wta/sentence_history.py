import uuid
from .sentence import Sentence
from .utils.nlp import retrieve_match_range, retrieve_affected_tokens
from tqdm import tqdm

class SentenceHistoryGenerator:

    def __init__(self, tpsfs, nlp_model):
        self.tpsfs = tpsfs
        self.nlp_model = nlp_model
        self.sentence_history = {}
        self.generate_sentence_history()
        self.filtered_sentence_history = {}
        self.filter_sentence_history()

    def generate_sentence_history(self):
        global_new_sens = []
        progress = tqdm(self.tpsfs, 'Generating sentence history')
        for tpsf in progress:
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
        self.sentence_history = self.eliminate_duplicates(self.sentence_history)

    @staticmethod
    def eliminate_duplicates(self, sentence_history):
        sentence_history_duplicates_eliminated = {}
        for id, sens in sentence_history.items():
            sens_duplicates_eliminated = []
            for s in sens:
                if s.text not in [sde.text for sde in sens_duplicates_eliminated]:
                    sens_duplicates_eliminated.append(s)
                else:
                    continue
            sentence_history_duplicates_eliminated[id] = sens_duplicates_eliminated
        return sentence_history_duplicates_eliminated

    def filter_sentence_history(self):
        progress = tqdm(self.sentence_history.items(), 'Filtering sentence history')
        for id, sen_versions in progress:
            self.filtered_sentence_history[id] = []
            prev_sv = None
            # for filtered sentence history, take only the sentence versions which contain text
            sen_versions = [sv for sv in sen_versions if sv.text != '' and sv.text is not None]
            for senid, sv in enumerate(sen_versions):
                if prev_sv is not None:
                    affected_tokens = retrieve_affected_tokens(prev_sv.text, sv.text)
                else:
                    affected_tokens = retrieve_affected_tokens('', sv.text)
                edit_distance, is_any_tok_oov, is_any_tok_typo, morphosyntactic_relevance = self.nlp_model.analyse_affected_tokens(affected_tokens, 0)
                if morphosyntactic_relevance and edit_distance and edit_distance > 1:
                    self.filtered_sentence_history[id].append(sv)
                elif morphosyntactic_relevance and not edit_distance:
                    self.filtered_sentence_history[id].append(sv)
                if senid == len(sen_versions)-1 and sv is not None and sv not in self.filtered_sentence_history[id]:
                    self.filtered_sentence_history[id].append(sv)
                prev_sv = sv

