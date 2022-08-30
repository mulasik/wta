import json, os, re
from .transformation import DependencyTransformation, ConstituencyTransformation


class TransformationClassifier:

    def __init__(self, sen_parses_path, file_name):
        self.sen_parses_path = sen_parses_path
        self.file_name = file_name


class DependencyTransformationClassifier(TransformationClassifier):

    def __init__(self, sen_history_dependency_relations, sen_parses_path, file_name):
        super().__init__(sen_parses_path, file_name)
        sen_history_dependency_transformations = {}
        for sen_id, dependency_relations in sen_history_dependency_relations.items():
            dependency_transformations = self.compare_dependency_relations(dependency_relations)
            if dependency_transformations:
                sen_history_dependency_transformations[sen_id] = dependency_transformations
        if sen_history_dependency_transformations:
            self.export_dependency_relations_impact_list(sen_history_dependency_transformations)
        else:
            print(f'INFO: No transformations found.')

    def compare_dependency_relations(self, dependency_relations):
        dependency_transformations = []
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
                    dependency_transformations.append(trans)
        return dependency_transformations

    def export_dependency_relations_impact_list(self, sen_history_dependency_transformations):
        json_file_path = os.path.join(self.sen_parses_path, 'dependency', self.file_name + '_dep_transformations.json')
        sen_history_dependency_transformations_dict = {}
        for sen_id, dts in sen_history_dependency_transformations.items():
            sen_history_dependency_transformations_dict[sen_id] = [dt.__dict__ for dt in dts]
        with open(json_file_path, 'w') as f:
            json.dump(sen_history_dependency_transformations_dict, f)


class ConsituencyTransformationClassifier(TransformationClassifier):

    def __init__(self, sen_history_constituency, sen_parses_path, file_name):
        super().__init__(sen_parses_path, file_name)
        sen_history_consituency_transformations = {}
        for sen_id, constituents in sen_history_constituency.items():
            constituents_transformations = self.compare_constituents(constituents)
            if constituents_transformations:
                sen_history_consituency_transformations.update({sen_id: constituents_transformations})
        if sen_history_consituency_transformations:
            self.export_constituency_impact_list(sen_history_consituency_transformations)
        else:
            print(f'INFO: No transformations found.')

    def compare_constituents(self, sen_history_constituent_parses):
        constituency_transformations = []
        for version_id, parse in sen_history_constituent_parses.items():
            # print(parse)
            parse_wo_tokens = re.sub(r'\(_ [A-ZÜÖÄa-züöä]+\)', '()', str(parse))
            # print(parse_wo_tokens)
            if version_id > 0:
                prev_parse = sen_history_constituent_parses[version_id - 1]
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
        return constituency_transformations

    def export_constituency_impact_list(self, sen_history_constituency_transformations: dict):
        json_file_path = os.path.join(self.sen_parses_path, 'constituency', self.file_name + '_const_transformations.json')
        sen_history_constituency_transformations_dict = {}
        for sen_id, dts in sen_history_constituency_transformations.items():
            sen_history_constituency_transformations_dict[sen_id] = [dt.__dict__ for dt in dts]
        with open(json_file_path, 'w') as f:
            json.dump(sen_history_constituency_transformations_dict, f)

