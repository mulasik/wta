import os
import errno
import json
from abc import ABC, abstractmethod

import settings
import paths
from .utils.other import ensure_path


class Names:

    TEXTHIS = 'text_history'
    JSON = 'json'
    TXT = 'txt'
    STATS = 'statistics'
    SENHIS = 'sentence_histories'
    SENPAR = 'sentence_parses'
    TRANSHIS = 'transformation_histories'
    DEP = 'dependency'
    CONST = 'constituency'
    VISUAL = 'visualisations'


class StorageSettings:

    @classmethod
    def set_paths(self):
        paths.texthis_dir = os.path.join(settings.config['output'], Names.TEXTHIS)
        paths.texthis_json_dir = os.path.join(paths.texthis_dir, Names.JSON)
        paths.texthis_txt_dir = os.path.join(paths.texthis_dir, Names.TXT)
        paths.texthis_visual_dir = os.path.join(paths.texthis_dir, Names.VISUAL)
        paths.stats_dir = os.path.join(settings.config['output'], Names.STATS)
        paths.senhis_dir = os.path.join(settings.config['output'], Names.SENHIS)
        paths.senhis_json_dir = os.path.join(paths.senhis_dir, Names.JSON)
        paths.senhis_txt_dir = os.path.join(paths.senhis_dir, Names.TXT)
        paths.senhis_visual_dir = os.path.join(paths.senhis_dir, Names.VISUAL)
        paths.senhis_parses_dir = os.path.join(paths.senhis_dir, Names.SENPAR)
        paths.dependency_senhis_parses_dir = os.path.join(paths.senhis_parses_dir, Names.DEP)
        paths.constituency_senhis_parses_dir = os.path.join(paths.senhis_parses_dir, Names.CONST)
        paths.transhis_dir = os.path.join(paths.senhis_dir, Names.TRANSHIS)
        paths.dependency_transhis_dir = os.path.join(paths.transhis_dir, Names.DEP)
        paths.constituency_transhis_dir = os.path.join(paths.transhis_dir, Names.CONST)
        paths_to_ensure = [d for d in dir(paths) if d.endswith('_dir')]
        for p in paths_to_ensure:
            ensure_path(getattr(paths, p))


class BaseStorage(ABC):

    @abstractmethod
    def process_texthis(self, tpsfs: list, mode: str, filtered=False):
        pass

    @abstractmethod
    def process_senhis(self, sen_hist: dict, view_mode='normal', filtered=False):
        pass


class ParsesStorage(ABC):

    @abstractmethod
    def process_dependency_parses(self, senhis_parses: dict, output_path: str):
        pass

    @abstractmethod
    def process_constituency_parses(self, senhis_parses: dict, output_path: str):
        pass


class TranshisStorage(ABC):

    @abstractmethod
    def process_transhis(self, transhis: dict, grammar: str):
        pass


class StatsStorage(ABC):

    @abstractmethod
    def process_stats(self):
        pass


class Json(BaseStorage, TranshisStorage):

    def process_texthis(self, tpsfs: list, mode: str, filtered=False):
        tpsf_list = [tpsf.to_dict() for tpsf in tpsfs]
        filter_label = '' if not filtered else '_filtered'
        json_file = f'{settings.filename}_{Names.TEXTHIS}_{mode}{filter_label}.json'
        json_file_path = os.path.join(paths.texthis_json_dir, json_file)
        with open(json_file_path, 'w') as f:
            json.dump(tpsf_list, f)

    def process_senhis(self, senhis: dict, view_mode='normal', filtered=False):
        view_mode_name = '' if view_mode == 'normal' else f'_{view_mode}'
        filter_label = '' if not filtered else '_filtered'
        json_file = f'{settings.filename}_{Names.SENHIS}{view_mode_name}{filter_label}.json'
        json_file_path = os.path.join(paths.senhis_json_dir, json_file)
        _senhis = {}
        for id, sens in senhis.items():
            _senhis[id] = [s.to_dict(view_mode) for s in sens]
        with open(json_file_path, 'w') as f:
            json.dump(_senhis, f)

    def process_transhis(self, transhis: dict, grammar: str):
        json_file = f'{settings.filename}_{Names.TRANSHIS}_{grammar}.json'
        output_dir = paths.dependency_transhis_dir if grammar == 'dependency' else paths.constituency_transhis_dir
        json_file_path = os.path.join(output_dir, json_file)
        _transhis = {}
        for sen_id, th in transhis.items():
            _transhis[sen_id] = [t.__dict__ for t in th]
        with open(json_file_path, 'w') as f:
            json.dump(_transhis, f)


class Txt(BaseStorage, ParsesStorage, StatsStorage):

    def process_texthis(self, tpsfs: list, mode: str, filtered=False):
        filter_label = '' if not filtered else '_filtered'
        txt_file = f'{settings.filename}_{Names.TEXTHIS}_{mode}{filter_label}.txt'
        txt_file_path = os.path.join(paths.texthis_txt_dir, txt_file)
        with open(txt_file_path, 'w') as f:
            for tpsf in tpsfs:
                f.write(tpsf.to_text())

    def process_senhis(self, senhis: dict, view_mode='normal', filtered=False):
        view_mode_name = '' if view_mode == 'normal' else f'_{view_mode}'
        filter_label = '' if not filtered else '_filtered'
        txt_file = f'{settings.filename}_{Names.SENHIS}{view_mode_name}{filter_label}.txt'
        txt_file_path = os.path.join(paths.senhis_txt_dir, txt_file)
        with open(txt_file_path, 'w') as f:
            for id, sens in senhis.items():
                f.write(f'''
******* {id} *******
''')
                for s in sens:
                    f.write(s.to_text(view_mode))

    def process_dependency_parses(self, senhis_parses: dict):
        for sen_id, sgl_senhis_parses in senhis_parses.items():
            output_path = os.path.join(paths.dependency_senhis_parses_dir, f'{sen_id}')
            ensure_path(output_path)
            for senver_id, sgl_parse in enumerate(sgl_senhis_parses):
                output_file = os.path.join(output_path, f'{senver_id}.txt')
                with open(output_file, 'w') as f:
                    for tok in sgl_parse:
                        f.write(f'{tok["id"]}\t{tok["word"]}\t{tok["pos"]}\t{tok["head"]}\t{tok["dep_rel"]}\n')

    def process_constituency_parses(self, senhis_parses: dict):
        for sen_id, sgl_senhis_parses in senhis_parses.items():
            output_path = os.path.join(paths.constituency_senhis_parses_dir, f'{sen_id}')
            ensure_path(output_path)
            for senver_id, parsed_sen in enumerate(sgl_senhis_parses):
                output_file = os.path.join(output_path, f'{senver_id}.txt')
                with open(output_file, 'w') as f:
                    f.write(f'{str(parsed_sen)}\n')

    def process_stats(self, b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx: str):
        source_file = settings.filename + '.idfx'
        task_name = os.path.split(os.path.split(idfx)[0])[-1]
        user_name = settings.filename.split('_', 1)[0]
        txt_file_path = os.path.join(paths.stats_dir, settings.filename + '_basic_statistics.txt')
        with open(txt_file_path, 'w') as f:
            f.write(f"""TASK: {task_name}
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
""")


class Svg(BaseStorage, TranshisStorage, StatsStorage):

    def process_texthis(self, tpsfs: list, mode: str, filtered=False):
        ...

    def process_senhis(self, sen_hist: dict, view_mode='normal', filtered=False):
        ...

    def process_transhis(self, transhis: dict, grammar: str):
        ...

    def process_stats(self):
        ...

