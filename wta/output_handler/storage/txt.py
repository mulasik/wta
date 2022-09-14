import os

import paths
import settings
from wta.output_handler.names import Names
from .base import BaseStorage
from wta.utils.other import ensure_path


class Txt(BaseStorage):

    def preprocess_data(self):
        pass

    def to_file(self):
        with open(self.filepath, 'w') as f:
            f.write(self.output_str)


class TexthisTxt(Txt):

    def __init__(self, data, mode='ecm', filtered=False):
        self.output_str = self.preprocess_data(data)
        filter_label = '' if not filtered else '_filtered'
        txt_file = f'{settings.filename}_{Names.TEXTHIS}_{mode}{filter_label}.txt'
        self.filepath = os.path.join(paths.texthis_txt_dir, txt_file)

    def preprocess_data(self, texthis) -> str:
        output_str = ''
        for tpsf in texthis:
            output_str += f'{tpsf.to_text()}\n'
        return output_str


class SenhisTxt(Txt):

    def __init__(self, data, view_mode='normal', filtered=False):
        self.output_str = self.preprocess_data(data, view_mode)
        view_mode_name = '' if view_mode == 'normal' else f'_{view_mode}'
        filter_label = '' if not filtered else '_filtered'
        txt_file = f'{settings.filename}_{Names.SENHIS}{view_mode_name}{filter_label}.txt'
        self.filepath = os.path.join(paths.senhis_txt_dir, txt_file)

    def preprocess_data(self, senhis: dict, view_mode: str) -> str:
        output_str = ''
        for id, sens in senhis.items():
            output_str += f'\n******* {id} *******\n'
            for s in sens:
                output_str += f'{s.to_text(view_mode)}\n\n'
        return output_str


class StatsTxt(Txt):

    def __init__(self, b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx: str) -> str:
        self.output_str = self.preprocess_data(b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx)
        txt_file_path = os.path.join(paths.stats_dir, settings.filename + '_basic_statistics.txt')
        self.filepath = os.path.join(paths.senhis_txt_dir, txt_file_path)

    def preprocess_data(self, b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx: str):
        source_file = settings.filename + '.idfx'
        task_name = os.path.split(os.path.split(idfx)[0])[-1]
        user_name = settings.filename.split('_', 1)[0]
        return f"""TASK: {task_name}
USER: {user_name}
SOURCE FILE: {source_file}

- EVENTS IN THE LOG FILE -
            Number events of type keyboard, replacement, insert: {e_stats.data['num_events']}
            Number keystrokes: {e_stats.data['num_keystrokes']} 
            Number replacements: {e_stats.data['num_replacements']}
            Number insert events: {e_stats.data['num_insertions']}

- TEXT VERSIONS -
            Number text versions in edit capturing mode (unfiltered): {b_stats.data['num_tpsfs']}
            Number text versions in edit capturing mode (filtered): {b_stats.data['num_tpsfs_filtered']}
            Number text versions in pause capturing mode: {b_stats.data['num_tpsfs_pcm']}

- PAUSES -
            Average pauses duration: {p_stats.data['avg_duration']}
            Maximum pauses duration: {p_stats.data['max_duration']}
            Minimum pauses duration: {p_stats.data['min_duration']}

- TRANSFORMING SEQUENCES -
            Number transforming sequences: {ts_stats.data['num_nonempty_ts']} 
            Average transforming sequence length: {ts_stats.data['avg_ts_len']}
            Number insertions: {ts_stats.data['num_ins']}
            Number inserted characters: {ts_stats.data['num_ins_chars']}
            Number deletions: {ts_stats.data['num_dels']}
            Number deleted characters: {ts_stats.data['num_del_chars']}
            Number appends: {ts_stats.data['num_apps']}
            Number appended characters: {ts_stats.data['num_app_chars']}

- SENTENCES -
            Number detected sentences in total: {sen_stats.data['detected_sens']}
            Number sentences in the final text: {sen_stats.data['final_num_sentences']}
            Potentially erroneous sentences due to segmentation problems: {sen_stats.data['num_potentially_erroneous_sens']}
            Maximum number sentence versions: {sen_stats.data['max_num_sen_versions']} 
            The sentence with most versions: "{sen_stats.data['sen_with_most_versions']}
            Mean number sentence versions: {sen_stats.data['mean_num_sentence_versions']}
            Number unchanged sentences: {sen_stats.data['num_unchanged_sens']}
"""


class ParsesTxt(Txt):

    def __init__(self, data, output_dir):
        self.output_dir = output_dir
        self.output = self.preprocess_data(data)

    def preprocess_data(self, senhis_parses: dict):
        output = []
        for sen_id, sgl_senhis_parses in senhis_parses.items():
            output_path = os.path.join(self.output_dir, f'{sen_id}')
            ensure_path(output_path)
            for senver_id, parsed_sen in enumerate(sgl_senhis_parses):
                output_filepath = os.path.join(output_path, f'{senver_id}.txt')
                output_str = self.generate_str(parsed_sen)
                output.append((output_filepath, output_str))
        return output

    def generate_str(self, parsed_sen):
        raise NotImplementedError

    def to_file(self):
        for o in self.output:
            with open(o[0], 'w') as f:
                f.write(o[1])


class DepParsesTxt(ParsesTxt):

    def __init__(self, data):
        super().__init__(data, paths.dependency_senhis_parses_dir)

    def generate_str(self, parsed_sen):
        output_str = ''
        for tok in parsed_sen:
            output_str += f'{tok["id"]}\t{tok["word"]}\t{tok["pos"]}\t{tok["head"]}\t{tok["dep_rel"]}\n'
        return output_str


class ConstParsesTxt(ParsesTxt):

    def __init__(self, data):
        super().__init__(data, paths.constituency_senhis_parses_dir)

    def generate_str(self, parsed_sen):
        return f'{str(parsed_sen)}\n'

