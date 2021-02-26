import uuid
from .sentence import Sentence


class SentenceHistoryGenerator:

    def __init__(self, tpsfs):
        self.tpsfs = tpsfs
        self.sentence_history = {}
        self.generate_sentence_history()

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
                            ns.set_revision_relevance(revision_relevance)
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
                        sentence_remains = Sentence(None, None, None, ds.revision_id, None, None)
                        sentence_remains.set_label(label)
                        sentence_remains.set_revision_relevance(revision_relevance)
                        self.sentence_history[id].append(sentence_remains)
            for us in unchanged_sens:
                us.set_revision_relevance(revision_relevance)
                for id, sens in self.sentence_history.items():
                    sens_texts = [sen.text for sen in sens]
                    if us.text in sens_texts:
                        self.sentence_history[id].append(us)

    def filter_sentence_history_wo_unchanged(self):
        filtered_sentence_history = {}
        for id, sen_versions in self.sentence_history.items():
            filtered_sentence_history[id] = []
            for sv in sen_versions:
                if sv.label != 'unchanged':
                    if sv.label != 'modified':
                        filtered_sentence_history[id].append(sv)
                    elif sv.label == 'modified' and sv.revision_relevance is True:
                        filtered_sentence_history[id].append(sv)
                    else:
                        continue
            # add the last sentence version
            last_sentence_version = sen_versions[-1]
            if last_sentence_version.text not in [sv.text for sv in filtered_sentence_history[id]]:
                filtered_sentence_history[id].append(last_sentence_version)
        return filtered_sentence_history

    def filter_sentence_history(self):
        filtered_sentence_history = {}
        for id, sen_versions in self.sentence_history.items():
            filtered_sentence_history[id] = []
            for sv in sen_versions:
                if sv.label == 'new' or (sv.label != 'unchanged' and sv.revision_relevance is True):
                    filtered_sentence_history[id].append(sv)
            # add the last sentence version
            last_sentence_version = sen_versions[-1]
            if last_sentence_version.text not in [sv.text for sv in filtered_sentence_history[id]]:
                filtered_sentence_history[id].append(last_sentence_version)
        for id, sen_versions in filtered_sentence_history.items():
            for svid, sv in enumerate(sen_versions):
                if sv.label == 'new' and sv.revision_relevance is False and len(sen_versions) > svid + 1 and \
                        sen_versions[svid + 1].label != 'deleted':
                    del sen_versions[svid]
        return filtered_sentence_history

