import argparse
import errno
import os
import sys
import traceback
from importlib import import_module

import settings
from wta.pipeline.text_history.idfx_parser import IdfxParser
from .models import SpacyModel
from wta.pipeline.sentence_histories.sentence_history import SentenceHistoryGenerator
from wta.pipeline.statistics.statistics_factory import StatisticsFactory
from wta.pipeline.sentence_parsing.parsers import Parsers
from wta.pipeline.sentence_parsing.facade import ParsingFacade
from wta.pipeline.sentence_parsing.models import Grammars
from wta.output_handler.plots.senhis_plot import SenhisPlot
from wta.output_handler.storage.output_factory import TexthisOutputFactory, SenhisOutputFactory, StatsOutputFactory, ParseOutputFactory


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

            print(f'\nProcessing the input file {idfx}...')

            # GENERATE TEXTHIS
            print('\n== KEYSTROKE LOGS PROCESSING & TEXT HISTORY GENERATION ==')
            idfx_parser = IdfxParser(idfx)
            idfx_parser.run()
            idfx_parser.filter_tpsfs_ecm()
            texthis = idfx_parser.all_tpsfs_ecm
            texthis_pcm = idfx_parser.all_tpsfs_pcm
            texthis_fltr = idfx_parser.filtered_tpsfs_ecm
            TexthisOutputFactory.run(texthis, texthis_pcm, texthis_fltr)

            # GENERATE SENHIS
            print('\n== SENTENCE HISTORIES GENERATION ==')
            senhis_generator = SentenceHistoryGenerator(idfx_parser.all_tpsfs_ecm)
            senhis = senhis_generator.sentence_history
            senhis_fltr = senhis_generator.filtered_sentence_history
            SenhisOutputFactory.run(senhis, senhis_fltr)

            # PARSE SENHIS
            print('\n== SENTENCE HISTORIES SYNTACTIC PARSING ==')
            dep_parser = ParsingFacade(senhis, Parsers.SUPAR, config['language'], Grammars.DEP)
            dep_parser.run()
            const_parser = ParsingFacade(senhis, Parsers.SUPAR, config['language'], Grammars.CONST)
            const_parser.run()
            ParseOutputFactory.run(dep_parser.senhis_parses, const_parser.senhis_parses)

            # GENERATE TRANSHIS
            print('\n== TRANSFORMATION HISTORIES GENERATION ==')
            # dep_trans_classifier = DependencyTransformationFactory(dep_parser.senhis_parses)
            # json_storage.process_transhis(dep_trans_classifier.transformation_history, 'dependency')
            # const_trans_classifier = ConsituencyTransformationFactory(const_parser.senhis_parses)
            # json_storage.process_transhis(const_trans_classifier.transformation_history, Grammars.CONST)
            # visualisation.visualise_dependency_relations_impact()
            # visualisation.visualise_consituents_impact()
            # visualisation.visualise_syntactic_impact()

            # GENERATE STATS
            b_stats, e_stats, p_stats, ts_stats, sen_stats = StatisticsFactory.run(idfx, texthis, texthis_fltr, texthis_pcm, senhis)
            StatsOutputFactory.run(b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx)


            #  PLOT
            tpsfs_to_visualise = [tpsf for tpsf in texthis if (
                    len(tpsf.new_sentences) > 0
                    or len(tpsf.modified_sentences) > 0
                    or len(tpsf.deleted_sentences) > 0)]
            visualisation = SenhisPlot(tpsfs_to_visualise, senhis)
            plt = visualisation.run()
            # visualisation.visualise_sentence_history(tpsfs_to_visualise, sentence_history)
            # if idfx_parser.filtered_tpsfs_ecm:
            # visualisation_filtered = VisualBase('_filtered')
            # visualisation_filtered.visualise_filtered_text_history(idfx_parser.filtered_tpsfs_ecm)
            # visualisation_filtered.visualise_sentence_history(idfx_parser.filtered_tpsfs_ecm, sentence_history)
            # else:
            # print(f"No relevant tpsfs found for: {idfx}", file=sys.stderr)
            # visualisation.visualise_statistics(idfx_parser.all_tpsfs_ecm, sentence_history)

        except:
            e = sys.exc_info()[0]
            traceback.print_exc()
            print(f"Failed for {idfx}", file=sys.stderr)
