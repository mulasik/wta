import argparse
import sys
from importlib import import_module
import os
import errno
from .idfx_parser import IdfxParser
from .sentence_history import SentenceHistoryGenerator
from .visualisation import Visualisation
from .export import (export_tpsfs_to_json, export_tpsfs_to_txt,
                     export_sentence_history_to_json,
                     export_sentence_history_to_json_simplified,
                     export_sentence_history_to_txt,
                     export_sentence_history_to_txt_extended)
from .stats_generator import generate_statistics
from .sentence_parser import SentenceParser
from .transformation_classifier import DependencyTransformationClassifier, ConsituencyTransformationClassifier
from .console_output import output_revisions_number
from .models import SpacyModel
import traceback


def load_path(dotted_path):
    parts = dotted_path.split('.')
    module = import_module('.'.join(parts[:-1]))
    attr = getattr(module, parts[-1])
    return attr


def ensure_path(path):
    try:
        os.makedirs(path)
    except OSError as err:
        if err.errno == errno.EEXIST:
            pass
        else:
            raise


ECM = 'Edit Capturing Mode'
PCM = 'Pause Capturing Mode'


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args(sys.argv[1:])

    config = load_path(args.config)

    nlp_model = SpacyModel(config['language'])

    for idfx in config['xml']:
        try:
            print(f'\nProcessing the input file {idfx}...')

            ensure_path(config['output'])
            file_name = os.path.split(idfx)[-1].replace('.idfx', '')
            sentence_histories_dir = f'{file_name}_sentence_histories'
            text_history_dir = f'{file_name}_text_history'
            stats_dir = f'{file_name}_statistics'
            ensure_path(os.path.join(config['output'], sentence_histories_dir))
            ensure_path(os.path.join(config['output'], text_history_dir))
            ensure_path(os.path.join(config['output'], stats_dir))

            # generate text history
            print('\n== KEYSTROKE LOGS PROCESSING ==')
            idfx_parser = IdfxParser(idfx, config, nlp_model)
            idfx_parser.run()

            # export text history in PCM and ECM
            export_tpsfs_to_json(idfx_parser.all_tpsfs_ecm, ECM, config['output'], file_name, nlp_model)
            export_tpsfs_to_txt(idfx_parser.all_tpsfs_ecm, config['output'], file_name, nlp_model)
            export_tpsfs_to_json(idfx_parser.all_tpsfs_pcm, PCM, config['output'], file_name, nlp_model)

            # generate sentence history
            sentence_history_generator = SentenceHistoryGenerator(idfx_parser.all_tpsfs_ecm, nlp_model)
            sentence_history = sentence_history_generator.sentence_history
            filtered_sentence_history = sentence_history_generator.filtered_sentence_history

            # export sentence history
            export_sentence_history_to_json(sentence_history, config['output'], file_name, nlp_model)
            export_sentence_history_to_json(filtered_sentence_history, config['output'], file_name, nlp_model, '_filtered')
            export_sentence_history_to_json_simplified(sentence_history, config['output'], file_name, nlp_model)
            export_sentence_history_to_json_simplified(filtered_sentence_history, config['output'], file_name, nlp_model,'_filtered')
            export_sentence_history_to_txt(sentence_history, config['output'], file_name, nlp_model)
            export_sentence_history_to_txt(filtered_sentence_history, config['output'], file_name, nlp_model, '_filtered')
            export_sentence_history_to_txt_extended(sentence_history, config['output'], file_name, nlp_model)
            export_sentence_history_to_txt_extended(filtered_sentence_history, config['output'], file_name, nlp_model, '_filtered')

            # visualise text and sentence history
            tpsfs_to_visualise = [tpsf for tpsf in idfx_parser.all_tpsfs_ecm if (len(tpsf.new_sentences) > 0 or len(tpsf.modified_sentences) > 0 or len(tpsf.deleted_sentences) > 0)]
            visualisation = Visualisation(config['output'], file_name)
            visualisation.visualise_text_history(tpsfs_to_visualise)
            visualisation.visualise_sentence_history(tpsfs_to_visualise, sentence_history)

            output_revisions_number(idfx_parser.all_tpsfs_ecm, ECM, False)
            output_revisions_number(idfx_parser.all_tpsfs_pcm, PCM, False)

            # generate filtered outputs
            idfx_parser.filter_tpsfs_ecm()
            if idfx_parser.filtered_tpsfs_ecm:
                export_tpsfs_to_json(idfx_parser.filtered_tpsfs_ecm, ECM, config['output'], file_name, nlp_model, '_filtered')
                export_tpsfs_to_txt(idfx_parser.filtered_tpsfs_ecm, config['output'], file_name, nlp_model, '_filtered')
                output_revisions_number(idfx_parser.filtered_tpsfs_ecm, ECM, True)
                visualisation_filtered = Visualisation(config['output'], file_name, '_filtered')
                visualisation_filtered.visualise_filtered_text_history(idfx_parser.filtered_tpsfs_ecm)
                visualisation_filtered.visualise_sentence_history(idfx_parser.filtered_tpsfs_ecm, sentence_history)
            else:
                print(f"No relevant tpsfs found for: {idfx}", file=sys.stderr)

            # generate basic statistics from <...>_output_ecm.json and visualise them
            generate_statistics(idfx, config['output'], file_name)

            # perform sentence parsing and identify syntactic impact
            print('\n== SENTENCE SYNTACTIC PARSING ==')
            sen_parser = SentenceParser(config['output'], file_name)
            dep_trans_classifier = DependencyTransformationClassifier(sen_parser.sen_history_dependency_relations, sen_parser.sen_parses_path, sen_parser.file_name)
            const_trans_classifier = ConsituencyTransformationClassifier(sen_parser.sen_history_constituency, sen_parser.sen_parses_path, sen_parser.file_name)
            visualisation.visualise_dependency_relations_impact()
            visualisation.visualise_consituents_impact()
            visualisation.visualise_syntactic_impact()

        except:
            e = sys.exc_info()[0]
            traceback.print_exc()
            print(f"Failed for {idfx}", file=sys.stderr)
