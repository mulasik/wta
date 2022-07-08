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
        self.perform_dependency_parsing(supar_dependency_pipeline, sen_histories)
        self.perform_constituency_parsing(supar_constiuency_pipeline, sen_histories)

    def perform_dependency_parsing(self, supar_dependency_pipeline, sen_histories):
        print(f'Performing dependency parsing on {len(sen_histories)} sentences...')
        dependency_relations_impact_list = {}
        for sen_id, sen_hist in sen_histories.items():
            print('===========')
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
            dependency_relations_comparison = self.compare_dependency_relations(dependency_relations)
            dependency_relations_impact_list.update({sen_id: dependency_relations_comparison})
        self.export_dependency_relations_impact_list(dependency_relations_impact_list)

    def retrieve_dependency_information(self, sen_history_dependencies):
        dependency_relations = {}
        for ver_id, words in sen_history_dependencies.items():
            dependency_relations.update({ver_id: []})
            for i, word in enumerate(words):
                word_details = word.split('\t')
                if len(word_details) > 1:
                    dep_rels = {
                        'id': word_details[0],
                        'head': word_details[6],
                        'dep': word_details[7]
                    }
                    dependency_relations[ver_id].append(dep_rels)
        # print(dependency_relations)
        return dependency_relations

    def compare_dependency_relations(self, dependency_relations):
        dependency_relations_comparison = {}
        for version_id, word_dep_rels in dependency_relations.items():
            dependency_relations_comparison[version_id] = {
                'prev_version_id': None,
                'dependency_relations_impacted': None
            }
            if version_id > 0:
                dependency_relations_comparison[version_id]['prev_version_id'] = version_id - 1
                for i, word in enumerate(word_dep_rels):
                    try:
                        # the dependency relation has changed
                        if word != dependency_relations[version_id - 1][i]:
                            dependency_relations_comparison[version_id]['dependency_relations_impacted'] = True
                        else:
                            dependency_relations_comparison[version_id]['dependency_relations_impacted'] = False
                    # the tree has been extended
                    except IndexError:
                        dependency_relations_comparison[version_id]['dependency_relations_impacted'] = True
        return dependency_relations_comparison

    def export_dependency_relations_impact_list(self, dependency_relations_impact_list):
        json_file_path = os.path.join(self.sen_parses_path, 'dependency', self.file_name + '_dependency_relations_impact.json')
        with open(json_file_path, 'w') as f:
            json.dump(dependency_relations_impact_list, f)

    def perform_constituency_parsing(self, supar_constiuency_pipeline, sen_histories):
        print(f'Performing constituency parsing on {len(sen_histories)} sentences...')
        constituency_impact_list = {}
        for sen_id, sen_hist in sen_histories.items():
            print('===========')
            print(f'Processing the sentence {sen_id}')
            consituency_parses_output_path = os.path.join(self.sen_parses_path, 'constituency', f'{sen_id}')
            ensure_path(consituency_parses_output_path)
            sentence_history = []
            for sen in sen_hist:
                if sen['text']:
                    sentence_history.append(sen['text'])
            supar_parser = SuParWrapper(supar_constiuency_pipeline, sentence_history, consituency_parses_output_path, None)
            sen_history_constituency = supar_parser.parse_constituency()
            constituents_comparison = self.compare_constituents(sen_history_constituency)
            constituency_impact_list.update({sen_id: constituents_comparison})
        self.export_constituency_impact_list(constituency_impact_list)

    def compare_constituents(self, sen_history_constituent_parses):
        constituents_comparison = {}
        for version_id, parse in sen_history_constituent_parses.items():
            # print(parse)
            parse_wo_tokens = re.sub(r'\(_ [A-ZÜÖÄa-züöä]+\)', '()', str(parse))
            print(parse_wo_tokens)
            constituents_comparison[version_id] = {
                'prev_version_id': None,
                'constituents_impacted': None
            }
            if version_id > 0:
                constituents_comparison[version_id]['prev_version_id'] = version_id - 1
                prev_parse = sen_history_constituent_parses[version_id - 1]
                prev_parse_wo_tokens = re.sub(r'\(_ [A-ZÜÖÄa-züöä]+\)', '()', str(prev_parse))
                try:
                    # the constituents have changed
                    if parse_wo_tokens != prev_parse_wo_tokens:
                        constituents_comparison[version_id]['constituents_impacted'] = True
                        print(True)
                    else:
                        constituents_comparison[version_id]['constituents_impacted'] = False
                        print(False)
                # the tree has been extended
                except IndexError:
                    constituents_comparison[version_id]['constituents_impacted'] = True
        return constituents_comparison

    def export_constituency_impact_list(self, constituency_impact_list):
        json_file_path = os.path.join(self.sen_parses_path, 'constituency', self.file_name + '_constituency_impact.json')
        with open(json_file_path, 'w') as f:
            json.dump(constituency_impact_list, f)


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
            # constituency_parse.pretty_print()
            # print(constituency_parse)
            output_file = os.path.join(self.output_path, f'{i}.txt')
            with open(output_file, 'w') as f:
                f.write(f'{constituency_parse}\n')
            sen_history_constituency.update({i: constituency_parse})
            # t = Tree.fromstring(str(s_tree))
            # t.pretty_print()
            # output_file = os.path.join(self.const_trees_output_path, 'supar', f'{i}.ps')
            # ensure_path(os.path.join(self.const_trees_output_path, 'supar'))
            # TreeView(t)._cframe.print_to_file(output_file)
        return sen_history_constituency
