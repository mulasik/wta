import argparse
import json
import shutil
import sys
import traceback
from importlib import import_module
from pathlib import Path
from typing import cast

from wta.pipeline.sentence_histories.sentencehood_evaluator import SentencehoodEvaluator

# from wta.pipeline.sentence_parsing.facade import ParsingFacade
# from wta.pipeline.sentence_parsing.models import Grammars, Parsers
from .config_data import ConfigData
from .language_models.spacy import SpacyModel
from .output_handler.output_factory import (
    ActionGroupsOutputFactory,
    ActionsOutputFactory,
    EventsOutputFactory,
    SenhisOutputFactory,
    SenhoodhisOutputFactory,
    StatsOutputFactory,
    TexthisFltrOutputFactory,
    TexthisOutputFactory,
    TpsfsOutputFactory,
    TpsfsPCMOutputFactory,
    TssOutputFactory,
)
from .pipeline.evaluation.texthis_correctness import check_texthis_correctness
from .pipeline.sentence_histories.sentence_history import SentenceHistoryGenerator
from .pipeline.statistics.statistics_factory import StatsFactory
from .pipeline.text_history.action_factory import ActionAggregator, ActionFactory
from .pipeline.text_history.event_factory import EventFactory
from .pipeline.text_history.tpsf_factory import ECMFactory, PCMFactory, filter_tpsfs
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

    correctly_processed: list[str] = []

    all_errors = {}

    for i, logfile in enumerate(config["ksl_files"]):
        try:
            filename = logfile.with_suffix("").name
            settings = Settings(config, nlp_model, filename)

            print(
                f"\nProcessing the input file {logfile}... ({i+1} out of {len(config['ksl_files'])})"
            )

            # GENERATE TEXTHIS
            print("\n== KEYSTROKE LOGS PROCESSING & TEXT HISTORY GENERATION ==")
            events = EventFactory().run(logfile, settings)
            EventsOutputFactory.run(events, settings)
            actions = ActionFactory().run(events)
            ActionsOutputFactory.run(actions, settings)
            tpsfs_pcm = PCMFactory().run(actions, settings)
            TpsfsPCMOutputFactory.run(tpsfs_pcm, settings)
            action_groups = ActionAggregator.run(actions)
            ActionGroupsOutputFactory.run(action_groups, settings)
            tss = TsFactory().run(action_groups, settings)
            TssOutputFactory.run(tss, settings)
            tpsfs = ECMFactory().run(tss, settings)
            TpsfsOutputFactory.run(tpsfs, settings)
            TexthisOutputFactory.run(tpsfs, settings)  # + texthis_pcm
            tpsfs_fltr = filter_tpsfs(tpsfs)
            TexthisFltrOutputFactory.run(tpsfs_fltr, settings)
            print("\n== TEXT HISTORY EVALUATION ==")
            correct = check_texthis_correctness(tpsfs[-1], filename, settings)
            if correct:
                correctly_processed.append(logfile.name)
                cp_dir = Path(
                    settings.config["ksl_files"][0].parents[1], "correctly_processed"
                )
                cp_dir.mkdir(exist_ok=True)
                cp_path = Path(cp_dir, logfile.name)
                shutil.copy(logfile, cp_path)
            print(
                f"{len(correctly_processed)} idfx files processed successfully so far: The final version of the text corresponds to the original text."
            )

            # GENERATE SENHIS
            print("\n== SENTENCE HISTORIES GENERATION ==")
            senhis_generator = SentenceHistoryGenerator()
            senhis = senhis_generator.run(tpsfs, settings)
            senhis_fltr = senhis_generator.filter_senhis(senhis)
            SenhisOutputFactory.run(tpsfs, tpsfs_fltr, senhis, senhis_fltr, settings)
            senhoodhis, error_details = SentencehoodEvaluator().run(
                senhis, nlp_model, settings
            )
            for e_cat, e_list in error_details.items():
                if e_cat not in all_errors:
                    all_errors[e_cat] = e_list
                else:
                    for e in e_list:
                        all_errors[e_cat].add(e)
            SenhoodhisOutputFactory.run(senhoodhis, settings)

            # TODO: PARSE SENHIS  # noqa: TD003, FIX002, TD002
            # print('\n== SENTENCE HISTORIES SYNTACTIC PARSING ==')
            # dep_parser = ParsingFacade(senhis, Parsers.SUPAR, config['language'], Grammars.DEP)
            # dep_parser.run()
            # const_parser = ParsingFacade(senhis, Parsers.SUPAR, config['language'], Grammars.CONST)
            # const_parser.run()
            # ParseOutputFactory.run(dep_parser.senhis_parses, const_parser.senhis_parses, settings)
            #
            # TODO: GENERATE TRANSHIS  # noqa: TD003, FIX002, TD002
            # print('\n== TRANSFORMATION HISTORIES GENERATION ==')
            # dep_transhis_classifier = DependencyTransformationFactory(dep_parser.senhis_parses)
            # const_transhis_classifier = ConsituencyTransformationFactory(const_parser.senhis_parses)
            # TranshisOutputFactory.run(dep_transhis_classifier.transhis, const_transhis_classifier.transhis, settings)
            #
            # GENERATE STATS
            print("\n== STATISTICS GENERATION ==")
            print("Generating statistics...")
            b_stats, e_stats, p_stats, ts_stats, sen_stats = StatsFactory().run(
                logfile, tpsfs, tpsfs_fltr, tpsfs_pcm, actions, senhis
            )
            StatsOutputFactory.run(
                b_stats,
                e_stats,
                p_stats,
                ts_stats,
                sen_stats,
                logfile,
                tpsfs,
                senhis,
                settings,
            )

        except:  # noqa: PERF203
            traceback.print_exc()
            print(f"Failed for {logfile}", file=sys.stderr)

    # print(all_errors)

    print("\n== FINAL TEXT HISTORY EVALUATION ==")
    print(
        f"{len(correctly_processed)} idfx files processed successfully: The final version of the text corresponds to the original text."
    )


if __name__ == "__main__":
    run()
