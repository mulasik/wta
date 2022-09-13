import re
import tqdm

from .transformation import DependencyTransformation, ConstituencyTransformation


class TransformationFactory:

    def __init__(self, senhis_parses, grammar):
        self.senhis_parses = senhis_parses
        self.grammar = grammar
        self.transhis = {}
        self.identify_transformations()

    def identify_transformations(self):
        pass


class DependencyTransformationFactory(TransformationFactory):

    def __init__(self, parsed_senhis):
        super().__init__(parsed_senhis, 'dependency')

    def identify_transformations(self):
        sen_dependency_transformations = []
        progress = tqdm.tqdm(self.senhis_parses.items(), 'Generating dependency transformation histories')
        for sen_id, sgl_senhis_parses in progress:
            for senver_id, parsed_sen in enumerate(sgl_senhis_parses):
                if senver_id > 0:
                    prev_senver_id = senver_id - 1
                    prev_parsed_sen = sgl_senhis_parses[prev_senver_id]
                    for i, word in enumerate(parsed_sen):
                        try:
                            # the dependency relation has changed
                            prev_word = sgl_senhis_parses[senver_id - 1][i]
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
                        trans = DependencyTransformation(senver_id, parsed_sen, prev_senver_id, prev_parsed_sen, dep_impacted, word_modified)
                        sen_dependency_transformations.append(trans)
            if sen_dependency_transformations:
                self.transhis[sen_id] = sen_dependency_transformations


class ConsituencyTransformationFactory(TransformationFactory):

    def __init__(self, parsed_senhis):
        super().__init__(parsed_senhis, 'constituency')

    def identify_transformations(self):
        progress = tqdm.tqdm(self.senhis_parses.items(), 'Generating constituency transformation histories')
        constituency_transformations = []
        for sen_id, sgl_senhis_parses in progress:
            for senver_id, parsed_sen in enumerate(sgl_senhis_parses):
                parse_wo_tokens = re.sub(r'\(_ [A-ZÜÖÄa-züöä]+\)', '()', str(parsed_sen))
                if senver_id > 0:
                    prev_senver_id = senver_id - 1
                    prev_parsed_sen = sgl_senhis_parses[prev_senver_id]
                    prev_parse_wo_tokens = re.sub(r'\(_ [A-ZÜÖÄa-züöä]+\)', '()', str(prev_parsed_sen))
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
                        const = ConstituencyTransformation(senver_id, str(parsed_sen), senver_id - 1, str(prev_parsed_sen), const_impacted)
                        constituency_transformations.append(const)
            if constituency_transformations:
                self.transhis[sen_id] = constituency_transformations

