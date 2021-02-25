import argparse
import sys
from importlib import import_module
import os

from .idfx_parser import IdfxParser
from .sentence_history import SentenceHistoryGenerator
from .export import export_tpsfs_to_json, export_tpsfs_to_txt, output_tpsfs_to_console, export_sentence_history_to_json, output_sentence_history_to_console, output_revisions_number


def load_path(dotted_path):
    parts = dotted_path.split('.')
    module = import_module('.'.join(parts[:-1]))
    attr = getattr(module, parts[-1])
    return attr

ECM = 'Edit Capturing Mode'
PCM = 'Pause Capturing Mode'


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args(sys.argv[1:])

    config = load_path(args.config)

    for idfx in config['xml']:
        print(f'\n{idfx}\n')

        # generate TPSFs
        parser = IdfxParser(idfx, config['pause_duration'], config['edit_distance'], config['filtering'])
        parser.run()
        file_name = os.path.split(idfx)[-1].replace('.idfx', '')

        #ECM
        export_tpsfs_to_json(parser.all_tpsfs_ecm, ECM, config['output'], file_name)
        export_tpsfs_to_txt(parser.all_tpsfs_ecm, config['output'], file_name)
        output_tpsfs_to_console(parser.all_tpsfs_ecm)
        output_revisions_number(parser.all_tpsfs_ecm, ECM, False)

        #PCM
        export_tpsfs_to_json(parser.all_tpsfs_pcm, PCM, config['output'], file_name)
        output_revisions_number(parser.all_tpsfs_pcm, PCM, False)

        #generate sentence history
        sentence_history_generator = SentenceHistoryGenerator(parser.all_tpsfs_ecm)
        sentence_history = sentence_history_generator.sentence_history
        filtered_sentence_history_wo_unchanged = sentence_history_generator.filter_sentence_history_wo_unchanged()
        export_sentence_history_to_json(sentence_history, config['output'], file_name)
        export_sentence_history_to_json(filtered_sentence_history_wo_unchanged, config['output'], file_name + '_filtered')
        output_sentence_history_to_console(filtered_sentence_history_wo_unchanged)

        if config['filtering'] is True:
            relevant_tpsfs = [tpsf for tpsf in parser.all_tpsfs_ecm if tpsf.morphosyntactic_relevance is True]
            export_tpsfs_to_json(relevant_tpsfs, ECM, config['output'], file_name, '_relevant')
            export_tpsfs_to_txt(relevant_tpsfs, config['output'], file_name, '_relevant')
            output_revisions_number(relevant_tpsfs, ECM, True)



