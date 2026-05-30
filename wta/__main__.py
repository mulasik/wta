import argparse
import shutil
import sys
import time
import traceback

# from collections.abc import Iterable
from importlib import import_module
from pathlib import Path
from typing import cast

# from bs4 import BeautifulSoup, Tag
# from wta.evaluation.sen_labels_correctness import check_sen_states_correctness
# from wta.evaluation.sen_ts_correctness import check_sen_ts_correctness, check_ts_length
from wta.pipeline.burst_layer.bursthis_generator import BursthisGenerator
from wta.pipeline.burst_layer.pcm_factory import PCMFactory

# from wta.pipeline.names import TUState
from wta.pipeline.sentence_layer.sentence_histories.sentence_history import SentenceHistory

# from wta.pipeline.sentence_layer.sentence_histories.sentencehood_evaluator import SentencehoodEvaluator
# from wta.pipeline.sentence_layer.sentence_histories.spsf import Spsf
from wta.pipeline.sentence_layer.sentence_parsing.facade import ParsingFacade
from wta.pipeline.sentence_layer.sentence_parsing.models import Grammars, Parsers

# from wta.pipeline.sentence_layer.syntactic_transformations.transformation_factory import (
#     ConsituencyTransformationFactory,
#     DependencyTransformationFactory,
# )
from wta.tests_and_evaluation.texthis_correctness import check_texthis_correctness

# from wta.pipeline.sentence_layer.sentence_histories.sentencehood_evaluator import SentencehoodEvaluator
# from wta.pipeline.sentence_parsing.facade import ParsingFacade
# from wta.pipeline.sentence_parsing.models import Grammars, Parsers
from .config_data import ConfigData
from .language_models.spacy import SpacyModel
from .output_handler.output_factory import (
    ActionGroupsOutputFactory,
    ActionsOutputFactory,
    BurstListOutputFactory,
    EventsOutputFactory,
    IdfxEventsOutputFactory,
    ParseOutputFactory,
    SenhisOutputFactory,
    # SenhoodhisOutputFactory,
    StatsOutputFactory,
    TexthisFltrOutputFactory,
    TexthisOutputFactory,
    TpsfsOutputFactory,
    TpsfsPCMOutputFactory,
    # TranshisOutputFactory,
    TssOutputFactory,
)
from .pipeline.preprocessing.action_factory import ActionAggregator, ActionFactory
from .pipeline.preprocessing.event_factory import EventFactory
from .pipeline.sentence_layer.sentence_histories.senhis_generator import SentenceHistoryGenerator
from .pipeline.transformation_layer.tpsf_factory import TpsfFactory, filter_tpsfs
from .pipeline.transformation_layer.tsbuilder_factory import TsBuilderFactory
from .settings import Settings
from .statistics.statistics_factory import StatsFactory


def load_path(dotted_path: str) -> ConfigData:
    parts = dotted_path.split(".")
    module = import_module(".".join(parts[:-1]))
    return cast(ConfigData, getattr(module, parts[-1]))

def _process_logfile(i: int, logfile: Path, config: ConfigData, nlp_model: SpacyModel, correctly_processed: list[str], incorrectly_processed: list[str]) -> None:
        try:
            filename = logfile.with_suffix("").name
            file_id = logfile.name.split(".")[0]
            settings = Settings(config, nlp_model, filename)
            print(
                f"\nProcessing the input file {logfile}... ({i+1} out of {len(config['ksl_files'])})"
            )

            # PROCESS KEYSTROKE LOGS TO GENERATE TRANSFORMING SEQUENCES
            print("\n============ KEYSTROKE LOGS PROCESSING ============")
            if settings.config["ksl_source_format"] in ["scriptlog_idfx", "inputlog_idfx"]:
                IdfxEventsOutputFactory.run(logfile, settings)
            events = EventFactory().run(logfile, settings)
            EventsOutputFactory.run(events, settings)
            actions = ActionFactory().run(events)
            ActionsOutputFactory.run(actions, settings)
            action_groups = ActionAggregator.run(actions, settings)
            ActionGroupsOutputFactory.run(action_groups, settings)
            tss = TsBuilderFactory().run(action_groups, settings)
            # all_files_tss.extend(list(tss))
            TssOutputFactory.run(tss, settings)

            # INITIALIZE BURST LAYER
            print("\n============ BURST LAYER (BL) INITIALIZATION ============")
            tpsfs_pcm = PCMFactory().run(actions, settings)
            TpsfsPCMOutputFactory.run(tpsfs_pcm, settings)

            # GENERATE TRANSFORMATION LAYER & PERFORM SL AND BL PROJECTONS
            print("\n============ TRANSFORMATION LAYER (TL) GENERATION & PROJECTION OF SL AND BL ============")
            tpsfs = TpsfFactory().run(tss, settings)
            TpsfsOutputFactory.run(tpsfs, settings)
            TexthisOutputFactory.run(tpsfs, settings)
            tpsfs_fltr = filter_tpsfs(tpsfs)
            TexthisFltrOutputFactory.run(tpsfs_fltr, settings)

            bursts = BursthisGenerator().run(tpsfs)
            BurstListOutputFactory.run(bursts, settings)

            # GENERATE SENTENCE LAYER & PERFORM L AND BL PROJECTONS
            print("\n============ SENTENCE LAYER (SL) GENERATION & PROJECTION OF TL AND BL ============")
            senhis_generator = SentenceHistoryGenerator()
            senhis = senhis_generator.run(tpsfs)
            # senhis_fltr = senhis_generator.filter_senhis(senhis)
            senhis_fltr: list[SentenceHistory] = []
            SenhisOutputFactory.run(tpsfs, tpsfs_fltr, senhis, senhis_fltr, settings)

            # EVALUATE SENTENCEHOOD
            # senhoodhis, error_details = SentencehoodEvaluator().run(
            #     senhis, nlp_model, settings
            # )
            # SenhoodhisOutputFactory.run(senhoodhis, settings)

            # PARSE SENHIS
            print("\n== SENTENCE HISTORIES SYNTACTIC PARSING ==")
            dep_senhis_parses = ParsingFacade().run(senhis, Parsers.SPACY, config["language"], Grammars.DEP)
            # const_senhis_parses = ParsingFacade().run(senhis, Parsers.SUPAR, config["language"], Grammars.CONST)
            ParseOutputFactory.run(file_id, dep_senhis_parses, settings) # const_senhis_parses

            # # GENERATE TRANSHIS
            # print('\n== TRANSFORMATION HISTORIES GENERATION ==')
            # dep_transhis_classifier = DependencyTransformationFactory(dep_senhis_parses)
            # const_transhis_classifier = ConsituencyTransformationFactory(const_senhis_parses)
            # TranshisOutputFactory.run(dep_transhis_classifier.transhis, settings) # const_transhis_classifier.transhis

            # GENERATE STATS
            print("\n============ STATISTICS GENERATION ============")
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

            # CHECK TEXT HISTORY EXTRACTION CORRECTNESS
            print("\n============ TEXT HISTORY EXTRACTION CHECK ============")
            correct = check_texthis_correctness(tpsfs[-1], filename, settings)
            if correct:
                correctly_processed.append(logfile.name)
                # cp_dir = Path(
                #     settings.config["ksl_files"][0].parents[1], "idfx_fully_processed",
                # )
                # cp_dir.mkdir(exist_ok=True)
                # cp_path = Path(cp_dir, logfile.name)
                # print(f"Moving {logfile} to {cp_path}...")
                # shutil.move(logfile, cp_path)
            else:
                incorrectly_processed.append(logfile.name)
                cp_dir = Path(
                    settings.config["ksl_files"][0].parents[1], "idfx_th_diffs"
                )
                cp_dir.mkdir(exist_ok=True)
                cp_path = Path(cp_dir, logfile.name)
                print(f"Moving {logfile} to {cp_path}...")
                shutil.move(logfile, cp_path)
            print(
                "\nSUMMARY:"
                f"\nText history generated correctly for {len(correctly_processed)} idfx file(s): \n{correctly_processed}"
                f"\nText history generated incorrectly for {len(incorrectly_processed)} idfx file(s): \n{incorrectly_processed}"
            )

        except (FileNotFoundError, PermissionError, OSError, ImportError, KeyError, ValueError, RuntimeError, TypeError, AttributeError) as e:
            traceback.print_exc()
            print(f"Failed for {logfile}: {e}", file=sys.stderr)
            # cp_dir = Path(
            #         settings.config["ksl_files"][0].parents[1], "idfx_errors"
            #     )
            # cp_dir.mkdir(exist_ok=True)
            # cp_path = Path(cp_dir, logfile.name)
            # print(f"Moving {logfile} to {cp_path}...")
            # shutil.move(logfile, cp_path)


def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    args = parser.parse_args(sys.argv[1:])
    config = load_path(args.config)
    nlp_model = SpacyModel(config["language"])

    correctly_processed: list[str] = []
    incorrectly_processed: list[str] = []

    start = time.time()
    for i, logfile in enumerate(config["ksl_files"]):
        _process_logfile(i, logfile, config, nlp_model, correctly_processed, incorrectly_processed)
    end = time.time()

    print("\n\n===============================================================================")
    print("======================= SUMMARY FOR ALL PROCESSED FILES =======================")
    print("===============================================================================\n\n")

    print(f"Total number of processed idfx files: {len(config['ksl_files'])}")
    print(f"Processing time: {(end - start)/60:.2f} minutes")

    print("\n** TEXT HISTORY **")
    print(
        f"\nText history generated correctly for {len(correctly_processed)} file(s): \n{correctly_processed}"
        f"\nText history generated incorrectly for {len(incorrectly_processed)} file(s): \n{incorrectly_processed}\n"
    )

if __name__ == "__main__":
    run()
