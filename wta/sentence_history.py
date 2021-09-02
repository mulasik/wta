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
            revision_relevance = tpsf.relevance
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
                            ns.set_revision_elevance(revision_relevance)
                            self.sentence_history[existing_id].append(ns)
                else:
                    uid = uuid.uuid1().int
                    ns.set_revision_relevance(revision_relevance)
                    self.sentence_history[uid] = [ns]
                global_new_sens.append(ns)
            for es in modified_sens:
                es.set_revision_relevance(revision_relevance)
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
                        sentence_remains = Sentence(None, None, None, ds.revision_id, None, None, self.nlp_model)
                        sentence_remains.set_label(label)
                        sentence_remains.set_revision_relevance(revision_relevance)
                        sen_tagged_tokens = self.nlp_model.tag_words(sentence_remains.text)
                        sentence_remains.set_tagged_tokens(sen_tagged_tokens)
                        self.sentence_history[id].append(sentence_remains)
            for us in unchanged_sens:
                us.set_revision_relevance(revision_relevance)
                for id, sens in self.sentence_history.items():
                    sens_texts = [sen.text for sen in sens]
                    if us.text in sens_texts:
                        self.sentence_history[id].append(us)
        self.sentence_history = self.eliminate_duplicates(self.sentence_history)

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
        irrelevant_ts_aggregated = []
        for id, sen_versions in progress:
            self.filtered_sentence_history[id] = []
            for senid, sv in enumerate(sen_versions):
                if sv.sentence_relevance is True:
                    sv.set_irrelevant_ts_aggregated(irrelevant_ts_aggregated)
                    self.filtered_sentence_history[id].append(sv)
                    irrelevant_ts_aggregated = []
                else:
                    if sv.sen_transforming_sequence is not None:
                        irrelevant_ts_aggregated.append((sv.sen_transforming_sequence.text, sv.sen_transforming_sequence.label))
                if senid == len(sen_versions)-1 and sv is not None and sv not in self.filtered_sentence_history[id]:
                    sv.set_irrelevant_ts_aggregated(irrelevant_ts_aggregated)
                    self.filtered_sentence_history[id].append(sv)
                    irrelevant_ts_aggregated = []

