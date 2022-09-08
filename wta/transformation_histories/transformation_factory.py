import re

from .transformation import DependencyTransformation, ConstituencyTransformation


class TransformationFactory:

    def __init__(self, parsed_senhis, grammar):
        self.parsed_senhis = parsed_senhis
        self.grammar = grammar
        self.transformation_history = {}
        self.identify_transformations()

    def identify_transformations(self):
        pass


class DependencyTransformationFactory(TransformationFactory):

    def __init__(self, parsed_senhis):
        super().__init__(parsed_senhis, 'dependency')

    def identify_transformations(self):
        sen_dependency_transformations = []
        for sen_id, dependency_relations in self.parsed_senhis.items():
            for version_id, word_dep_rels in dependency_relations.items():
                if version_id > 0:
                    for i, word in enumerate(word_dep_rels):
                        try:
                            # the dependency relation has changed
                            prev_word = dependency_relations[version_id - 1][i]
                            prev_word_deps = (prev_word['id'], prev_word['head'], prev_word['dep_rel'])
                            word_deps = (word['id'], word['head'], word['dep_rel'])
                            if word_deps != prev_word_deps:
                                dep_impacted = True
                            else:
                                dep_impacted = False
                                if word['word'] != prev_word['word']:
                                    word_modified = True
                                else:
                                    word_modified = False
                        # the tree has been extended
                        except IndexError:
                            dep_impacted = True
                    if dep_impacted or word_modified:
                        trans = DependencyTransformation(version_id, word_dep_rels, version_id - 1, dependency_relations[version_id - 1], dep_impacted, word_modified)
                        sen_dependency_transformations.append(trans)
            if sen_dependency_transformations:
                self.transformation_history[sen_id] = sen_dependency_transformations


class ConsituencyTransformationFactory(TransformationFactory):

    def __init__(self, parsed_senhis):
        super().__init__(parsed_senhis, 'constituency')

    def identify_transformations(self):
        for sen_id, constituents in self.parsed_senhis.items():
            constituency_transformations = []
            for version_id, parse in constituents.items():
                # print(parse)
                parse_wo_tokens = re.sub(r'\(_ [A-ZÜÖÄa-züöä]+\)', '()', str(parse))
                # print(parse_wo_tokens)
                if version_id > 0:
                    prev_parse = constituents[version_id - 1]
                    prev_parse_wo_tokens = re.sub(r'\(_ [A-ZÜÖÄa-züöä]+\)', '()', str(prev_parse))
                    try:
                        # the constituents have changed
                        if parse_wo_tokens != prev_parse_wo_tokens:
                            const_impacted = True
                        else:
                            const_impacted = False
                    # the tree has been extended
                    except IndexError:
                        const_impacted = True
                    if const_impacted:
                        const = ConstituencyTransformation(version_id, parse, version_id - 1, prev_parse, const_impacted)
                        constituency_transformations.append(const)
            if constituency_transformations:
                self.transformation_history[sen_id] = constituency_transformations

