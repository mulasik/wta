from collections.abc import Iterable
from pathlib import Path

from bs4 import Tag

from wta.pipeline.sentence_layer.sentence_histories.sentence_history import SentenceHistory
from wta.pipeline.sentence_layer.sentence_histories.sentencehood_evaluator import Sentencehood

# from wta.pipeline.SL2TL_projection.tssegmenter import TSSegmenter
from ...pipeline.preprocessing.action import Action
from ...pipeline.preprocessing.events.base import BaseEvent
from ...pipeline.sentence_layer.sentence_parsing.parsers import TokenProp
from ...pipeline.transformation_layer.tpsf import Tpsf, TpsfPCM
from ...pipeline.transformation_layer.ts import TSBuilder
from ...settings import Settings
from ...statistics.statistics import (
    BasicStatistics,
    EventStatistics,
    PauseStatistics,
    SentenceStatistics,
    TSStatistics,
)
from ...utils.other import ensure_path
from .. import names
from .base import BaseStorage


class Txt(BaseStorage):
    def __init__(self, filepath: Path, output_str: str) -> None:
        self.filepath = filepath
        self.output_str = output_str

    def to_file(self) -> None:
        self.filepath.write_text(self.output_str)


class IdfxTxt(Txt):
    def __init__(self, data: Iterable[Tag], settings: Settings) -> None:
        txt_file = f"{settings.filename}_{names.IDFX_EVENTS}.txt"
        super().__init__(
            settings.paths.idfx_events_dir / txt_file, self.preprocess_data(data)
        )

    def preprocess_data(self, events: Iterable[Tag]) -> str:
        output_str = ""
        for i, event in enumerate(events):
            event_type = event["type"]
            parts = event.find_all("part")
            if event_type == "replacement":
                wordlog = parts[0]
                startpos = int(wordlog.start.get_text())
                endpos = int(wordlog.end.get_text())
                text = wordlog.newtext.get_text()
                output_str += f"{event['type']}: *{text}* startpos: {startpos} - endpos: {endpos}\n\n"
            elif event_type == "selection":
                wordlog = parts[0]
                startpos = int(wordlog.start.get_text())
                endpos = int(wordlog.end.get_text())
                output_str += f"{event['type']}: startpos: {startpos} - endpos: {endpos}\n\n"
            elif event_type == "keyboard":
                wordlog = parts[0]
                winlog = parts[1]
                keyname = winlog.key.get_text()
                content = winlog.value.get_text()
                startpos = int(wordlog.position.get_text())
                starttime = float(winlog.starttime.get_text())/1000
                endtime = float(winlog.endtime.get_text())/1000
                # textlen = int(wordlog.documentlength.get_text())
                output_str += f"{i}: {event['type']} ({keyname}): *{content}* startpos: {startpos} ({starttime}-{endtime})\n\n"
                # print(starttime)
            else:
                output_str += f"{i}: Unknown event type: {event_type}\n\n"
        return output_str


class EventsTxt(Txt):
    def __init__(self, data: list[BaseEvent], settings: Settings) -> None:
        txt_file = f"{settings.filename}_{names.EVENTS}.txt"
        super().__init__(
            settings.paths.events_dir / txt_file, self.preprocess_data(data)
        )

    def preprocess_data(self, events: list[BaseEvent]) -> str:
        output_str = ""
        for event in events:
            if type(event).__name__ in ["ProductionKeyboardEvent", "DDeletionKeyboardEvent", "BDeletionKeyboardEvent"]:
                # if event.__dict__["preceding_pause"] is not None and event.__dict__["preceding_pause"] > 2.0:
                #     print(i, event.__dict__["preceding_pause"])
                output_str += f'{type(event).__name__}: *{event.__dict__["content"]}* {event.__dict__["startpos"]} {event.__dict__["endpos"]} {event.__dict__["starttime"]}-{event.__dict__["endtime"]} (pause before: {event.__dict__["preceding_pause"]})\n\n'
            else:
                output_str += f'{type(event).__name__}: *{event.__dict__["content"]}* {event.__dict__["startpos"]} {event.__dict__["endpos"]} {"Unknown"}-{"Unknown"} (pause before: {"Unknown"})\n\n'
        return output_str


class ActionsTxt(Txt):
    def __init__(self, data: list[Action], settings: Settings) -> None:
        txt_file = f"{settings.filename}_{names.ACTIONS}.txt"
        super().__init__(
            settings.paths.actions_dir / txt_file, self.preprocess_data(data)
        )

    def preprocess_data(self, actions: list[Action]) -> str:
        output_str = ""
        for a in actions:
            starttime = None if not hasattr(a, "starttime") else a.starttime
            endtime = None if not hasattr(a, "endtime") else a.endtime
            preceding_pause = None if not hasattr(a, "preceding_pause") else a.preceding_pause
            # if type(a).__name__ not in ["Replacement", "Pasting"]:
            output_str += (
                f"{type(a).__name__} ({a.startpos}:{a.endpos}) |{a.content}| {starttime}-{endtime} (pause before: {preceding_pause}))\n\n"
            )
            # else:
            #     output_str += (
            #         f"{type(a).__name__} ({a.startpos}:{a.endpos}) |{a.content}| Unknown-Unknown (pause before: Unknown))\n\n"
            #     )
        return output_str


class ActionGroupsTxt(Txt):
    def __init__(self, data: dict[str, list[Action]], settings: Settings) -> None:
        txt_file = f"{settings.filename}_{names.ACTION_GROUPS}.txt"
        super().__init__(
            settings.paths.actions_dir / txt_file, self.preprocess_data(data)
        )

    def preprocess_data(self, action_groups: dict[str, list[Action]]) -> str:
        output_str = ""
        for at, aa in action_groups.items():
            startpos = aa[0].startpos
            endpos = aa[-1].endpos
            starttime = getattr(aa[0], "starttime", None)
            endtime = getattr(aa[-1], "starttime", None)
            preceding_pause = getattr(aa[0], "preceding_pause", None)
            output_str += f'{at} * len {len(aa)} * ({startpos}:{endpos}) ({starttime}-{endtime}) (Pred pause: {preceding_pause})) \n*{"".join([a.__dict__["content"] for a in aa])}*\n\n'
        return output_str


class TssTxt(Txt):
    def __init__(self, data: list[TSBuilder], settings: Settings) -> None:
        txt_file = f"{settings.filename}_{names.TSS}.txt"
        super().__init__(settings.paths.tss_dir / txt_file, self.preprocess_data(data))

    def preprocess_data(self, tss: list[TSBuilder]) -> str:
        output_str = ""
        for ts in tss:
            preceding_pause = None if len(ts.pauses) == 0 else ts.pauses[0]
            output_str += f'{ts.label} (pos: {ts.startpos}-{ts.endpos}) (time: {ts.starttime}-{ts.endtime}) preceding pause: {preceding_pause} following pause: {ts.following_pause}: "{ts.text}"\n\n'
        return output_str


class TpsfsTxt(Txt):
    def __init__(self, data: list[Tpsf], settings: Settings) -> None:
        txt_file = f"{settings.filename}_{names.TPSFS}.txt"
        super().__init__(
            settings.paths.tpsfs_dir / txt_file, self.preprocess_data(data)
        )

    def preprocess_data(self, tpsfs: list[Tpsf]) -> str:
        output_str = ""
        for tpsf in tpsfs:
            tpsf_tus = (
                []
                if not tpsf.tus
                else [
                    f"({tu.state}) {tu.type}:   |{tu.text}|\n"
                    for tu in tpsf.tus
                ]
            )
            tus_str = ""
            for ttus in tpsf_tus:
                tus_str += f"{ttus}\n"
            # ts_str = f'The distance between the previous and the current point of inscription: {tpsf.ts_diff}.\n\n'
            # ts_str_no_change = 'Point of inscription unchanged.\n\n'
            # f'{ts_str if tpsf.ts_diff != 0 else ts_str_no_change}' \
            output_str += (
                f"======================{tpsf.id}====================\n\n"
                f"----------------TRANSFORMING SEQUENCE----------------\n\n"
                f"{tpsf.ts.label.upper()} ({tpsf.ts.startpos}-{tpsf.ts.endpos}):\n|{tpsf.ts.text}|\n"
                f"------------------------TEXT-------------------------\n\n"
                f"|{tpsf.text}|\n\n"
                f"----------------------TEXTUNITS----------------------\n\n"
                f"{tus_str}\n"
            )
        return output_str


class TpsfsPCMTxt(Txt):
    def __init__(self, data: list[TpsfPCM], settings: Settings) -> None:
        txt_file = f"{settings.filename}_{names.TPSFSPCM}.txt"
        super().__init__(
            settings.paths.tpsfs_dir / txt_file, self.preprocess_data(data)
        )

    def preprocess_data(self, tpsfs: list[TpsfPCM]) -> str:
        output_str = ""
        for tpsf in tpsfs:
            output_str += (
                f"======================{tpsf.revision_id}====================\n\n"
                f"PRECEDING PAUSE: {tpsf.pause}\n\n"
                f"|{tpsf.content}|\n\n"
            )
        return output_str


class TexthisTxt(Txt):
    def __init__(
        self,
        data: list[Tpsf],
        settings: Settings,
        mode: str = "ecm",
        filtered: bool = False,
    ) -> None:
        filter_label = "" if not filtered else "_filtered"
        txt_file = f"{settings.filename}_{names.TEXTHIS}_{mode}{filter_label}.txt"
        super().__init__(
            settings.paths.texthis_txt_dir / txt_file, self.preprocess_data(data)
        )

    def preprocess_data(self, texthis: list[Tpsf]) -> str:
        output_str = ""
        for tpsf in texthis:
            output_str += f"{tpsf!s}\n"
        return output_str


# class TextTranshisTxt(Txt):
#     def __init__(
#         self,
#         data: list[TSSegmenter],
#         settings: Settings,
#     ) -> None:
#         txt_file = f"{settings.filename}_{names.TEXT_TRANSHIS}.txt"
#         super().__init__(
#             settings.paths.text_transhis_txt_dir / txt_file, self.preprocess_data(data)
#         )

#     def preprocess_data(self, text_transhis: list[TSSegmenter]) -> str:
#         output_str = ""
#         for tt in text_transhis:
#             output_str += f"{tt!s}\n"
#         return output_str


class SenhisTxt(Txt):
    def __init__(
        self,
        data: list[SentenceHistory],
        settings: Settings,
        view_mode: str = "normal",
        filtered: bool = False,
    ) -> None:
        view_mode_name = "" if view_mode == "normal" else f"_{view_mode}"
        filter_label = "" if not filtered else "_filtered"
        txt_file = (
            f"{settings.filename}_{names.SENHIS}{view_mode_name}{filter_label}.txt"
        )
        super().__init__(
            settings.paths.senhis_txt_dir / txt_file,
            self.preprocess_data(data),
        )

    def preprocess_data(self, senhiss: list[SentenceHistory]) -> str:
        output_str = ""
        for senhis in senhiss:
            output_str += f"\n******* {senhis.sen_id} *******\n"
            for s in senhis.senversions:
                output_str += f"{s!s}\n\n"
        return output_str


class SenhoodhisTxt(Txt):
    def __init__(
        self,
        data: dict[int, list[Sentencehood]],
        settings: Settings,
    ) -> None:
        txt_file = f"{settings.filename}_{names.SENHOOD}.txt"
        super().__init__(
            settings.paths.senhood_txt_dir / txt_file,
            self.preprocess_data(data),
        )

    def preprocess_data(self, senhoodhis: dict[int, list[Sentencehood]]) -> str:
        output_str = ""
        for key, senhood_data in senhoodhis.items():
            output_str += f"\n******* {key} *******\n"
            for sh in senhood_data:
                output_str += f"""Sentence: |{sh.text}|
Completeness (mechanical-conceptual-syntactic): {sh.mech_completeness}-{sh.con_completeness}-{sh.syn_completeness}
Correctness (mechanical-grammatical): {sh.mech_correctness}-{sh.gram_correctness}\n\n"""
        return output_str


class StatsTxt(Txt):
    def __init__(
        self,
        b_stats: BasicStatistics,
        e_stats: EventStatistics,
        p_stats: PauseStatistics,
        ts_stats: TSStatistics,
        sen_stats: SentenceStatistics,
        idfx: Path,
        settings: Settings,
    ) -> None:
        txt_file_path = settings.paths.stats_dir / (
            settings.filename + "_basic_statistics.txt"
        )
        super().__init__(
            settings.paths.senhis_txt_dir / txt_file_path,
            self.preprocess_data(
                b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx, settings
            ),
        )

    def preprocess_data(
        self,
        b_stats: BasicStatistics,
        e_stats: EventStatistics,
        p_stats: PauseStatistics,
        ts_stats: TSStatistics,
        sen_stats: SentenceStatistics,
        idfx: Path,
        settings: Settings,
    ) -> str:
        source_file = settings.filename + ".idfx"
        task_name = idfx.parent.name
        user_name = settings.filename.split("_", 1)[0]
        return f"""TASK: {task_name}
USER: {user_name}
SOURCE FILE: {source_file}

- EVENTS IN THE LOG FILE -
            Number events of type keyboard, replacement, insert: {e_stats.data['num_events']}
            Number keystrokes: {e_stats.data['num_keystrokes']}
            Number replacements: {e_stats.data['num_replacements']}
            Number insert events: {e_stats.data['num_insertions']}

- TEXT VERSIONS -
            Number text versions in edit capturing mode (unfiltered): {b_stats.data['num_tpsfs']}
            Number text versions in edit capturing mode (filtered): {b_stats.data['num_tpsfs_filtered']}
            Number text versions in pause capturing mode: {p_stats.data['num_tpsfs']}

- PAUSES -
            Average pauses duration: {p_stats.data['avg_duration']} sec
            Maximum pauses duration: {p_stats.data['max_duration']} sec
            Minimum pauses duration: {p_stats.data['min_duration']} sec
            Events without pause information: {p_stats.data['events_wo_pause_info']}

- TRANSFORMING SEQUENCES -
            Number transforming sequences: {ts_stats.data['num_nonempty_ts']}
            Average transforming sequence length: {ts_stats.data['avg_ts_len']}
            Number insertions: {ts_stats.data['num_ins']}
            Number inserted characters: {ts_stats.data['num_ins_chars']}
            Number deletions: {ts_stats.data['num_dels']}
            Number deleted characters: {ts_stats.data['num_del_chars']}
            Number appends: {ts_stats.data['num_apps']}
            Number appended characters: {ts_stats.data['num_app_chars']}

- SENTENCES -
            Number detected sentences in total: {sen_stats.data['detected_sens']}
            Number sentences in the final text: {sen_stats.data['final_num_sentences']}
            Potentially erroneous sentences due to segmentation problems: {sen_stats.data['num_potentially_erroneous_sens']}
            Maximum number sentence versions: {sen_stats.data['max_num_sen_versions']}
            The sentence with most versions: "{sen_stats.data['sen_with_most_versions']}
            Mean number sentence versions: {sen_stats.data['mean_num_sentence_versions']}
            Number unchanged sentences: {sen_stats.data['num_unchanged_sens']}
"""


class ParsesTxt(Txt):
    def __init__(
        self, file_id: str, data: dict[int, list[list[TokenProp]]], output_dir: Path
    ) -> None:
        self.output_dir = output_dir
        self.output = self.preprocess_data(file_id, data)

    def preprocess_data(
        self, file_id: str, senhis_parses: dict[int, list[list[TokenProp]]]
    ) -> list[tuple[Path, str]]:
        output = []
        complete_output_str = ""
        for sen_id, sgl_senhis_parses in senhis_parses.items():
            for senver_id, parsed_sen in enumerate(sgl_senhis_parses):
                output_dir = self.output_dir / file_id
                ensure_path(output_dir)
                output_filepath = self.output_dir / file_id / f"{sen_id}.txt"
                single_output_str = self.generate_str(senver_id, parsed_sen)
                complete_output_str += single_output_str
                output.append((output_filepath, complete_output_str))
        return output

    def generate_str(self, senver_id: int, parsed_sen: list[TokenProp]) -> str:
        raise NotImplementedError

    def to_file(self) -> None:
        for path, content in self.output:
            path.write_text(content)


class DepParsesTxt(ParsesTxt):
    def __init__(
        self, file_id: str, data: dict[int, list[list[TokenProp]]], settings: Settings
    ) -> None:
        super().__init__(file_id, data, settings.paths.dependency_senhis_parses_dir)

    def generate_str(self, senver_id: int, parsed_sen: list[TokenProp]) -> str:
        output_str = f"{senver_id}\n"
        for tok in parsed_sen:
            output_str += f'{tok["id"]}\t{tok["word"]}\t{tok["pos"]}\t{tok["head"]}\t{tok["dep_rel"]}\n'
        output_str += "\n=====\n"
        return output_str


class ConstParsesTxt(ParsesTxt):
    def __init__(
        self, file_id: str, data: dict[int, list[list[TokenProp]]], settings: Settings
    ) -> None:
        super().__init__(file_id, data, settings.paths.constituency_senhis_parses_dir)

    def generate_str(self, senver_id: int, parsed_sen: list[TokenProp]) -> str:
        return f"{parsed_sen!s}\n"
