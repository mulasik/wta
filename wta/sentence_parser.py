import json
import os
from supar import Parser
import re
from nltk.tree import Tree
from nltk.draw import TreeView

from .utils.other import ensure_path


class SentenceParser:

    def __init__(self, output_path, file_name):
        self.output_path = output_path
        self.file_name = file_name
        print('Loading the dependency parser model...')
        supar_dependency_pipeline = Parser.load('biaffine-dep-xlmr')
        print('Loading the consituency parser model...')
        supar_constiuency_pipeline = Parser.load('crf-con-xlmr')
        self.sen_parses_path = os.path.join(output_path, f'{file_name}_sentence_histories', f'{file_name}_sentence_parses')
        ensure_path(self.sen_parses_path)
        sentence_histories_json = os.path.join(output_path, f'{file_name}_sentence_histories', f'{file_name}_sentence_history.json')
        with open(sentence_histories_json) as f:
            sen_histories = json.load(f)
        self.sen_history_dependency_relations = self.perform_dependency_parsing(supar_dependency_pipeline, sen_histories)
        self.sen_history_constituency = self.perform_constituency_parsing(supar_constiuency_pipeline, sen_histories)

    def perform_dependency_parsing(self, supar_dependency_pipeline, sen_histories):
        print(f'Performing dependency parsing on {len(sen_histories)} sentences...')
        sen_history_dependency_relations = {}
        for sen_id, sen_hist in sen_histories.items():
            print(f'Processing the sentence {sen_id}')
            dependency_parses_output_path = os.path.join(self.sen_parses_path, 'dependency', f'{sen_id}')
            ensure_path(dependency_parses_output_path)
            sentence_history = []
            for sen in sen_hist:
                if sen['text']:
                    sentence_history.append(sen['text'])
            supar_parser = SuParWrapper(supar_dependency_pipeline, sentence_history, dependency_parses_output_path, None)
            sen_history_dependencies = supar_parser.parse_dependency()
            dependency_relations = self.retrieve_dependency_information(sen_history_dependencies)
            sen_history_dependency_relations[sen_id] = dependency_relations
        return sen_history_dependency_relations

    def retrieve_dependency_information(self, sen_history_dependencies):
        dependency_relations = {}
        for ver_id, words in sen_history_dependencies.items():
            dependency_relations.update({ver_id: []})
            for i, word in enumerate(words):
                word_details = word.split('\t')
                if len(word_details) > 1:
                    dep_rels = {
                        'id': word_details[0],
                        'word': word_details[1],
                        'pos': word_details[3],
                        'head': word_details[6],
                        'dep_rel': word_details[7],
                    }
                    dependency_relations[ver_id].append(dep_rels)
        return dependency_relations

    def perform_constituency_parsing(self, supar_constiuency_pipeline, sen_histories):
        print(f'Performing constituency parsing on {len(sen_histories)} sentences...')
        sen_histories_constituency = {}
        for sen_id, sen_hist in sen_histories.items():
            print(f'Processing the sentence {sen_id}...')
            consituency_parses_output_path = os.path.join(self.sen_parses_path, 'constituency', f'{sen_id}')
            ensure_path(consituency_parses_output_path)
            sentence_history = []
            for sen in sen_hist:
                if sen['text']:
                    sentence_history.append(sen['text'])
            supar_parser = SuParWrapper(supar_constiuency_pipeline, sentence_history, consituency_parses_output_path, None)
            sen_history_constituency = supar_parser.parse_constituency()
            sen_histories_constituency[sen_id] = sen_history_constituency
        return sen_histories_constituency


class SuParWrapper:
    """
        SuPar returns the dependency parse in CoNLL-X format:
            - ID (index in sentence, starting at 1)
            - FORM (word form itself)
            - LEMMA (word's lemma or stem)
            - CPOSTAG
            - POSTAG
            - FEAT (list of morphological features separated by |)
            - HEAD (index of syntactic parent, 0 for ROOT)
            - DEPREL (syntactic relationship between HEAD and this word)
            - PHEAD
            - PDEPREL
        """

    def __init__(self, pipeline, sentence_history, output_path, const_trees_output_path):
        self.pipeline = pipeline
        self.sentence_history = sentence_history
        self.output_path = output_path
        self.const_trees_output_path = const_trees_output_path

    def parse_dependency(self):
        sen_history_dependencies = {}
        for i, sen_version in enumerate(self.sentence_history):
            dependency_parse = self.pipeline.predict(sen_version, lang='en', prob=True, verbose=False)
            words_lst = []
            output_file = os.path.join(self.output_path, f'{i}.txt')
            with open(output_file, 'w') as f:
                for s in dependency_parse:
                    words_lst = str(s).split('\n')
                    f.write(f'{s}\n')
            sen_history_dependencies.update({i: words_lst})
        return sen_history_dependencies

    def parse_constituency(self):
        sen_history_constituency = {}
        # one sentence history with multiple sentence versions
        for i, sen_version in enumerate(self.sentence_history):
            constituency_parse = self.pipeline.predict(sen_version, lang='en', prob=True, verbose=False)[0]
            output_file = os.path.join(self.output_path, f'{i}.txt')
            with open(output_file, 'w') as f:
                f.write(f'{str(constituency_parse)}\n')
            sen_history_constituency.update({i: str(constituency_parse)})
            # t = Tree.fromstring(str(s_tree))
            # t.pretty_print()
            # output_file = os.path.join(self.const_trees_output_path, 'supar', f'{i}.ps')
            # ensure_path(os.path.join(self.const_trees_output_path, 'supar'))
            # TreeView(t)._cframe.print_to_file(output_file)
        return sen_history_constituency

