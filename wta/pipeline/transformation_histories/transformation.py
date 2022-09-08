
class TransformationClass:
    REDUCTION = 'dependency tree reduction'
    EXTENSION = 'dependency tree extension'
    MODIFICATION = 'dependency tree modification'
    WORD_MODIFICATION = 'word-level modification'


class DependencyTransformation:

    def __init__(self, current_version_id, current_dep_rels, prev_version_id, prev_dep_rels, dep_impacted, word_modified):
        self.current_version_id = current_version_id
        self.current_dep_rels = current_dep_rels
        self.prev_version_id = prev_version_id
        self.prev_dep_rels = prev_dep_rels
        self.dep_impacted = dep_impacted
        self.word_modified = word_modified
        self.transformation_class = self.classify()

    def classify(self):
        """
        Classifies the transformation performed between two sentence versions.
        :return: a string containing transformation class
        """
        if self.dep_impacted:
            unchanged = [r for r in self.current_dep_rels if r in self.prev_dep_rels]
            delta_prev_cur = [r for r in self.prev_dep_rels if r not in unchanged]
            delta_cur_prev = [r for r in self.current_dep_rels if r not in unchanged]
            if len(delta_prev_cur) > 0 and len(delta_cur_prev) == 0:
                return TransformationClass.REDUCTION
            elif len(delta_prev_cur) == 0 and len(delta_cur_prev) > 0:
                return TransformationClass.EXTENSION
            elif len(delta_prev_cur) > 0 and len(delta_cur_prev) > 0:
                return TransformationClass.MODIFICATION
        if not self.dep_impacted and self.word_modified:
            return TransformationClass.WORD_MODIFICATION

    def find_best_match(self, word, word_list):
        """
        Searches for a word which has most attributes in common with the given word.
        The attributes are dependency annotations: id, word, POS, head, dep relation.
        :param word: word to find a match for
        :param word_list: list of potential matches for the given word
        :return: a dictionary containing the attr values of the matching item and the names of the matching attrs
        """
        max = 0
        for il in word_list:
            item_equal_attrs = self.find_equal_attrs(word, il)
            if len(item_equal_attrs) > max:
                max = len(item_equal_attrs)
                matching_item = il
                matching_attrs = item_equal_attrs
        return matching_item, matching_attrs

    @staticmethod
    def find_equal_attrs(w1, w2):
        """
        Compares dependency annotations of two words (id, word, POS, head, dep relation) to find equal attributes.
        :param w1: first word to compare
        :param w2: second word to compare
        :return: a list of attributes names which the words have in common
        """
        same_id = w1['id'] == w2['id']
        same_word = w1['word'] == w2['word']
        same_pos = w1['pos'] == w2['pos']
        same_head = w1['head'] == w2['head']
        same_dep_rel = w1['dep_rel'] == w2['dep_rel']
        res = {
            'same_id': same_id,
            'same_word': same_word,
            'same_pos': same_pos,
            'same_head': same_head,
            'same_dep_rel': same_dep_rel
        }
        equal_attrs = [key for key, val in res.items() if val is True]
        return equal_attrs


class ConstituencyTransformation:

    def __init__(self, current_version_id, current_contituents, prev_version_id, prev_constituents, const_impacted):
        self.current_version_id = current_version_id
        self.current_contituents = current_contituents
        self.prev_version_id = prev_version_id
        self.prev_constituents = prev_constituents
        self.const_impacted = const_impacted
        self.transformation_class = None




