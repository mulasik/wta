import argparse
import sys
from importlib import import_module
import os

from .idfx_parser import IdfxParser
from .sentence_history import SentenceHistoryGenerator
from .export import export_tpsfs_to_json, export_tpsfs_to_txt, output_tpsfs_to_console, export_sentence_history_to_json, output_sentence_history_to_console


def load_path(dotted_path):
    parts = dotted_path.split('.')
    module = import_module('.'.join(parts[:-1]))
    attr = getattr(module, parts[-1])
    return attr


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args(sys.argv[1:])

    config = load_path(args.config)

    for idfx in config['xml']:
        print(f'\n{idfx}\n')
        parser = IdfxParser(idfx, config['pause_duration'])
        parser.run()
        file_name = os.path.split(idfx)[-1].replace('.idfx', '')
        export_tpsfs_to_json(parser.all_tpsfs_ecm, 'Edit Capturing Mode', config['output'], file_name)
        export_tpsfs_to_json(parser.all_tpsfs_ecm, 'Pause Capturing Mode', config['output'], file_name)
        export_tpsfs_to_txt(parser.all_tpsfs_ecm, config['output'], file_name)
        output_tpsfs_to_console(parser.all_tpsfs_ecm)
        sentence_history_generator = SentenceHistoryGenerator(parser.all_tpsfs_ecm)
        sentence_history = sentence_history_generator.sentence_history
        export_sentence_history_to_json(sentence_history, config['output'], file_name)
        output_sentence_history_to_console(sentence_history)

