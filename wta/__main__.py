import argparse
import sys
import traceback
from importlib import import_module
from typing import cast

from .config_data import ConfigData
from .language_models.spacy import SpacyModel
from .output_handler.output_factory import (
    ActionGroupsOutputFactory,
    ActionsOutputFactory,
    EventsOutputFactory,
    TexthisOutputFactory,
    TpsfsOutputFactory,
    TssOutputFactory,
)
from .pipeline.text_history.action_factory import ActionAggregator, ActionFactory
from .pipeline.text_history.event_factory import EventFactory
from .pipeline.text_history.tpsf_factory import ECMFactory
from .pipeline.text_history.ts_factory import TsFactory
from .settings import Settings


def load_path(dotted_path: str) -> ConfigData:
    parts = dotted_path.split(".")
    module = import_module(".".join(parts[:-1]))
    return cast(ConfigData, getattr(module, parts[-1]))


def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    args = parser.parse_args(sys.argv[1:])
    config = load_path(args.config)
    nlp_model = SpacyModel(config["language"])

    for idfx in config["xml"]:
        try:
            filename = idfx.with_suffix("").name
            settings = Settings(config, nlp_model, filename)

            print(f"\nProcessing the input file {idfx}...")

            # GENERATE TEXTHIS
            print("\n== KEYSTROKE LOGS PROCESSING & TEXT HISTORY GENERATION ==")
            events = EventFactory().run(idfx)
            EventsOutputFactory.run(events, settings)
            actions = ActionFactory().run(events)
            ActionsOutputFactory.run(actions, settings)
            action_groups = ActionAggregator.run(actions)
            ActionGroupsOutputFactory.run(action_groups, settings)
            tss = TsFactory().run(action_groups)
            TssOutputFactory.run(tss, settings)
            tpsfs = ECMFactory().run(tss, settings)
            TpsfsOutputFactory.run(tpsfs, settings)
            TexthisOutputFactory.run(tpsfs, settings)  # + texthis_pcm
            # TODO: create text history in pause capturing mode, texthis_pcm = idfx_parser.all_tpsfs_pcm
            # TODO: filter text history, texthis_fltr = ECMFactory().filter(texthis, settings)
            # TODO: export filtered text history, TexthisFltrOutputFactory.run(texthis_fltr, settings)

            # TODO: GENERATE SENHIS
            # print('\n== SENTENCE HISTORIES GENERATION ==')
            # senhis = SentenceHistoryGenerator().run(tpsfs)
            # senhis_fltr = senhis_generator.filtered_sentence_history
            # SenhisOutputFactory.run(texthis, texthis_fltr, senhis, senhis_fltr, settings)
            #
            # TODO: PARSE SENHIS
            # print('\n== SENTENCE HISTORIES SYNTACTIC PARSING ==')
            # dep_parser = ParsingFacade(senhis, Parsers.SUPAR, config['language'], Grammars.DEP)
            # dep_parser.run()
            # const_parser = ParsingFacade(senhis, Parsers.SUPAR, config['language'], Grammars.CONST)
            # const_parser.run()
            # ParseOutputFactory.run(dep_parser.senhis_parses, const_parser.senhis_parses, settings)
            #
            # TODO: GENERATE TRANSHIS
            # print('\n== TRANSFORMATION HISTORIES GENERATION ==')
            # dep_transhis_classifier = DependencyTransformationFactory(dep_parser.senhis_parses)
            # const_transhis_classifier = ConsituencyTransformationFactory(const_parser.senhis_parses)
            # TranshisOutputFactory.run(dep_transhis_classifier.transhis, const_transhis_classifier.transhis, settings)
            #
            # TODO: GENERATE STATS
            # print('\n== STATISTICS GENERATION ==')
            # print('Generating statistics...')
            # b_stats, e_stats, p_stats, ts_stats, sen_stats = StatsFactory.run(idfx, texthis, texthis_fltr, texthis_pcm, senhis)
            # StatsOutputFactory.run(b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx, texthis, senhis, settings)

        except:
            traceback.print_exc()
            print(f"Failed for {idfx}", file=sys.stderr)


if __name__ == "__main__":
    run()
