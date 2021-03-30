import argparse
import sys
from importlib import import_module
import os

from .idfx_parser import IdfxParser
from .sentence_history import SentenceHistoryGenerator
from .visualisation import Visualisation
from .export import (export_tpsfs_to_json, export_tpsfs_to_txt, export_sentence_history_to_json, output_revisions_number, export_sentence_history_to_txt)


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
        print(f'\nProcessing the input file {idfx}...\n')

        # generate TPSFs
        idfx_parser = IdfxParser(idfx, config['pause_duration'], config['edit_distance'], config['filtering'])
        idfx_parser.run()
        file_name = os.path.split(idfx)[-1].replace('.idfx', '')

        # ECM
        export_tpsfs_to_json(idfx_parser.all_tpsfs_ecm, ECM, config['output'], file_name)
        export_tpsfs_to_txt(idfx_parser.all_tpsfs_ecm, config['output'], file_name)
        # output_tpsfs_to_console(idfx_parser.all_tpsfs_ecm)
        # output_revisions_number(idfx_parser.all_tpsfs_ecm, ECM, False)

        # PCM
        export_tpsfs_to_json(idfx_parser.all_tpsfs_pcm, PCM, config['output'], file_name)
        # output_revisions_number(idfx_parser.all_tpsfs_pcm, PCM, False)

        # generate sentence history
        sentence_history_generator = SentenceHistoryGenerator(idfx_parser.all_tpsfs_ecm)
        sentence_history = sentence_history_generator.sentence_history
        filtered_sentence_history = sentence_history_generator.filtered_sentence_history
        sentences_selected_for_reparsing = sentence_history_generator.sentences_selected_for_reparsing

        export_sentence_history_to_json(sentence_history, config['output'], file_name)
        export_sentence_history_to_json(filtered_sentence_history, config['output'], file_name, '_filtered')
        export_sentence_history_to_json(sentences_selected_for_reparsing, config['output'], file_name, '_filtered_for_reparsing')
        export_sentence_history_to_txt(sentence_history, config['output'], file_name)
        export_sentence_history_to_txt(filtered_sentence_history, config['output'], file_name, '_filtered')
        export_sentence_history_to_txt(sentences_selected_for_reparsing, config['output'], file_name, '_filtered_for_reparsing')
        # output_sentence_history_to_console(filtered_sentence_history)

        # visualise
        tpsfs_to_visualise = [tpsf for tpsf in idfx_parser.all_tpsfs_ecm if (len(tpsf.new_sentences) > 0 or len(tpsf.modified_sentences) > 0)]
        visualisation = Visualisation(config['output'], file_name)
        visualisation.visualise_text_history(tpsfs_to_visualise)
        visualisation.visualise_sentence_history(tpsfs_to_visualise, sentence_history)

        if config['filtering'] is True:
            relevant_tpsfs = [tpsf for tpsf in idfx_parser.all_tpsfs_ecm if (len(tpsf.new_sentences) > 0 or len(tpsf.modified_sentences) > 0) and tpsf.morphosyntactic_relevance is True]
            export_tpsfs_to_json(relevant_tpsfs, ECM, config['output'], file_name, '_filtered')
            export_tpsfs_to_txt(relevant_tpsfs, config['output'], file_name, '_filtered')
            output_revisions_number(relevant_tpsfs, ECM, True)
            visualisation_filtered = Visualisation(config['output'], file_name, '_filtered')
            visualisation_filtered.visualise_text_history(relevant_tpsfs)
            visualisation_filtered.visualise_sentence_history(relevant_tpsfs, sentence_history)

