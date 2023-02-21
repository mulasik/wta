class TransformationClass:
    REDUCTION = "dependency tree reduction"
    EXTENSION = "dependency tree extension"
    MODIFICATION = "dependency tree modification"
    WORD_MODIFICATION = "word-level modification"


class Transformation:
    def __init__(
        self,
        cur_senver_id,
        cur_parsed_sen,
        prev_senver_id,
        prev_parsed_sen,
        syntactic_impact,
    ):
        self.cur_senver_id = cur_senver_id
        self.cur_parsed_sen = cur_parsed_sen
        self.prev_senver_id = prev_senver_id
        self.prev_parsed_sen = prev_parsed_sen
        self.syntactic_impact = syntactic_impact


class DependencyTransformation(Transformation):
    def __init__(
        self,
        cur_senver_id,
        cur_parsed_sen,
        prev_senver_id,
        prev_parsed_sen,
        dep_impacted,
        word_modified,
    ):
        super().__init__(
            cur_senver_id, cur_parsed_sen, prev_senver_id, prev_parsed_sen, dep_impacted
        )
        self.word_modified = word_modified
        self.transformation_class = self.classify()

    def classify(self):
        """
        Classifies the transformation performed between two sentence versions.
        :return: a string containing transformation class
        """
        if self.syntactic_impact:
            unchanged = [r for r in self.cur_parsed_sen if r in self.prev_parsed_sen]
            delta_prev_cur = [r for r in self.prev_parsed_sen if r not in unchanged]
            delta_cur_prev = [r for r in self.cur_parsed_sen if r not in unchanged]
            if len(delta_prev_cur) > 0 and len(delta_cur_prev) == 0:
                return TransformationClass.REDUCTION
            elif len(delta_prev_cur) == 0 and len(delta_cur_prev) > 0:
                return TransformationClass.EXTENSION
            elif len(delta_prev_cur) > 0 and len(delta_cur_prev) > 0:
                return TransformationClass.MODIFICATION
        if not self.syntactic_impact and self.word_modified:
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
        same_id = w1["id"] == w2["id"]
        same_word = w1["word"] == w2["word"]
        same_pos = w1["pos"] == w2["pos"]
        same_head = w1["head"] == w2["head"]
        same_dep_rel = w1["dep_rel"] == w2["dep_rel"]
        res = {
            "same_id": same_id,
            "same_word": same_word,
            "same_pos": same_pos,
            "same_head": same_head,
            "same_dep_rel": same_dep_rel,
        }
        return [key for key, val in res.items() if val is True]


class ConstituencyTransformation(Transformation):
    def __init__(
        self,
        cur_senver_id,
        cur_parsed_sen,
        prev_senver_id,
        prev_parsed_sen,
        const_impacted,
    ):
        super().__init__(
            cur_senver_id,
            cur_parsed_sen,
            prev_senver_id,
            prev_parsed_sen,
            const_impacted,
        )
