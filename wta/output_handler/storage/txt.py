import os

import paths
import settings
from wta.output_handler.storage.base import BaseStorage, ParsesStorage, StatsStorage, Names
from wta.utils.other import ensure_path


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