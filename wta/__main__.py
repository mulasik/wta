import argparse
import errno
import os
import sys
import traceback
from importlib import import_module

import settings
from wta.text_history.idfx_parser import IdfxParser
from .models import SpacyModel
from wta.sentence_histories.sentence_history import SentenceHistoryGenerator
from .statistics import StatisticsFactory
from .sentence_parsing.parsers import Parsers
from .sentence_parsing.facade import ParsingFacade
from wta.transformation_histories.transformation_factory import (DependencyTransformationFactory,
                                                                 ConsituencyTransformationFactory)
from .sentence_parsing.models import Grammars
from .visualisation import Visualisation
from .storage import StorageSettings, Json, Txt


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


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args(sys.argv[1:])
    config = load_path(args.config)
    nlp_model = SpacyModel(config['language'])

    settings.config = config
    settings.nlp_model = nlp_model

    for idfx in config['xml']:
        try:
            filename = os.path.split(idfx)[-1].replace('.idfx', '')
            settings.filename = filename
            StorageSettings.set_paths()

            print(f'\nProcessing the input file {idfx}...')

            # generate text history
            print('\n== KEYSTROKE LOGS PROCESSING ==')
            idfx_parser = IdfxParser(idfx)
            idfx_parser.run()

            # export text history in PCM and ECM
            json_storage = Json()
            txt_storage = Txt()
            json_storage.process_texthis(idfx_parser.all_tpsfs_ecm, 'ecm')
            txt_storage.process_texthis(idfx_parser.all_tpsfs_ecm, 'ecm')
            json_storage.process_texthis(idfx_parser.all_tpsfs_pcm, 'pcm')

            # generate sentence history
            sentence_history_generator = SentenceHistoryGenerator(idfx_parser.all_tpsfs_ecm)
            sentence_history = sentence_history_generator.sentence_history
            filtered_sentence_history = sentence_history_generator.filtered_sentence_history

            # export sentence history
            json_storage.process_senhis(sentence_history)
            json_storage.process_senhis(filtered_sentence_history, filtered=True)
            json_storage.process_senhis(sentence_history, view_mode='simplified')
            json_storage.process_senhis(filtered_sentence_history, view_mode='simplified', filtered=True)

            txt_storage.process_senhis(sentence_history)
            txt_storage.process_senhis(filtered_sentence_history, filtered=True)
            txt_storage.process_senhis(sentence_history, view_mode='extended')
            txt_storage.process_senhis(filtered_sentence_history, view_mode='extended', filtered=True)

            # visualise text and sentence history
            tpsfs_to_visualise = [tpsf for tpsf in idfx_parser.all_tpsfs_ecm if (
                        len(tpsf.new_sentences) > 0 or len(tpsf.modified_sentences) > 0 or len(
                    tpsf.deleted_sentences) > 0)]
            visualisation = Visualisation()
            visualisation.visualise_text_history(tpsfs_to_visualise)
            visualisation.visualise_sentence_history(tpsfs_to_visualise, sentence_history)

            # generate filtered outputs
            idfx_parser.filter_tpsfs_ecm()
            if idfx_parser.filtered_tpsfs_ecm:
                json_storage.process_texthis(idfx_parser.filtered_tpsfs_ecm, 'ecm', filtered=True)
                txt_storage.process_texthis(idfx_parser.filtered_tpsfs_ecm, 'ecm', filtered=True)
                visualisation_filtered = Visualisation('_filtered')
                visualisation_filtered.visualise_filtered_text_history(idfx_parser.filtered_tpsfs_ecm)
                visualisation_filtered.visualise_sentence_history(idfx_parser.filtered_tpsfs_ecm, sentence_history)
            else:
                print(f"No relevant tpsfs found for: {idfx}", file=sys.stderr)

            # generate basic statistics from <...>_output_ecm.json and visualise them
            b_stats, e_stats, p_stats, ts_stats, sen_stats = StatisticsFactory.run(idfx, idfx_parser.all_tpsfs_ecm, idfx_parser.filtered_tpsfs_ecm, idfx_parser.all_tpsfs_pcm, sentence_history)
            txt_storage.process_stats(b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx)
            visualisation.visualise_statistics(idfx_parser.all_tpsfs_ecm, sentence_history)

            # perform sentence parsing and identify syntactic impact
            print('\n== SENTENCE SYNTACTIC PARSING ==')
            dep_parser = ParsingFacade(sentence_history, Parsers.SUPAR, config['language'], Grammars.DEP)
            dep_parser.run()
            txt_storage.process_dependency_parses(dep_parser.senhis_parses)
            const_parser = ParsingFacade(sentence_history, Parsers.SUPAR, config['language'], Grammars.CONST)
            const_parser.run()
            txt_storage.process_constituency_parses(const_parser.senhis_parses)

            # generate transformation histories
            # dep_trans_classifier = DependencyTransformationFactory(dep_parser.senhis_parses)
            # json_storage.process_transhis(dep_trans_classifier.transformation_history, 'dependency')
            # const_trans_classifier = ConsituencyTransformationFactory(const_parser.senhis_parses)
            # json_storage.process_transhis(const_trans_classifier.transformation_history, Grammars.CONST)
            # visualisation.visualise_dependency_relations_impact()
            # visualisation.visualise_consituents_impact()
            # visualisation.visualise_syntactic_impact()

        except:
            e = sys.exc_info()[0]
            traceback.print_exc()
            print(f"Failed for {idfx}", file=sys.stderr)
