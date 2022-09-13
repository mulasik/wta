import argparse
import os
import sys
import traceback
from importlib import import_module

import settings
from wta.pipeline.text_history.idfx_parser import IdfxParser
from .models import SpacyModel
from wta.pipeline.sentence_histories.sentence_history import SentenceHistoryGenerator
from wta.pipeline.statistics.statistics_factory import StatsFactory
from wta.pipeline.sentence_parsing.parsers import Parsers
from wta.pipeline.sentence_parsing.facade import ParsingFacade
from wta.pipeline.sentence_parsing.models import Grammars
from wta.output_handler.output_factory import (TexthisOutputFactory, SenhisOutputFactory,
                                               StatsOutputFactory, ParseOutputFactory, TranshisOutputFactory)
from wta.pipeline.transformation_histories.transformation_factory import (DependencyTransformationFactory,
                                                                          ConsituencyTransformationFactory)


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
            SenhisOutputFactory.run(texthis, texthis_fltr, senhis, senhis_fltr)

            # PARSE SENHIS
            print('\n== SENTENCE HISTORIES SYNTACTIC PARSING ==')
            dep_parser = ParsingFacade(senhis, Parsers.SUPAR, config['language'], Grammars.DEP)
            dep_parser.run()
            const_parser = ParsingFacade(senhis, Parsers.SUPAR, config['language'], Grammars.CONST)
            const_parser.run()
            ParseOutputFactory.run(dep_parser.senhis_parses, const_parser.senhis_parses)

            # GENERATE TRANSHIS
            print('\n== TRANSFORMATION HISTORIES GENERATION ==')
            dep_transhis_classifier = DependencyTransformationFactory(dep_parser.senhis_parses)
            const_transhis_classifier = ConsituencyTransformationFactory(const_parser.senhis_parses)
            TranshisOutputFactory.run(dep_transhis_classifier.transhis, const_transhis_classifier.transhis)

            # GENERATE STATS
            print('\n== STATISTICS GENERATION ==')
            print('Generating statistics...')
            b_stats, e_stats, p_stats, ts_stats, sen_stats = StatsFactory.run(idfx, texthis, texthis_fltr, texthis_pcm, senhis)
            StatsOutputFactory.run(b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx, texthis, senhis)

        except:
            e = sys.exc_info()[0]
            traceback.print_exc()
            print(f"Failed for {idfx}", file=sys.stderr)

