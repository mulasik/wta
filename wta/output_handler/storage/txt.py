import os

import paths
import settings
from wta.pipeline.sentence_histories.text_unit import TextUnit
from wta.pipeline.sentence_parsing.parsers import TokenProp
from wta.pipeline.statistics.statistics import (
    BasicStatistics,
    EventStatistics,
    PauseStatistics,
    SentenceStatistics,
    TSStatistics,
)

from ...pipeline.text_history.action import Action
from ...pipeline.text_history.events.keyboard import KeyboardEvent
from ...pipeline.text_history.tpsf import TpsfECM
from ...pipeline.text_history.ts import TransformingSequence
from ...utils.other import ensure_path
from ..names import Names
from .base import BaseStorage


class Txt(BaseStorage):
    def __init__(self, filepath: str, output_str: str) -> None:
        self.filepath = filepath
        self.output_str = output_str

    def to_file(self) -> None:
        with open(self.filepath, "w") as f:
            f.write(self.output_str)


class EventsTxt(Txt):
    def __init__(self, data: list[KeyboardEvent]) -> None:
        txt_file = f"{settings.filename}_{Names.EVENTS}.txt"
        super().__init__(
            os.path.join(paths.events_dir, txt_file), self.preprocess_data(data)
        )

    def preprocess_data(self, events: list[KeyboardEvent]) -> str:
        output_str = ""
        for event in events:
            output_str += f'{type(event).__name__}: *{event.__dict__["content"]}* {event.__dict__["startpos"]} {event.__dict__["endpos"]}\n\n'
        return output_str


class ActionsTxt(Txt):
    def __init__(self, data: list[Action]) -> None:
        txt_file = f"{settings.filename}_{Names.ACTIONS}.txt"
        super().__init__(
            os.path.join(paths.actions_dir, txt_file), self.preprocess_data(data)
        )

    def preprocess_data(self, actions: list[Action]) -> str:
        output_str = ""
        for a in actions:
            output_str += (
                f"{type(a).__name__} ({a.startpos}:{a.endpos}) *{a.content}*\n\n"
            )
        return output_str


class ActionGroupsTxt(Txt):
    def __init__(self, data: dict[int, list[Action]]) -> None:
        txt_file = f"{settings.filename}_{Names.ACTION_GROUPS}.txt"
        super().__init__(
            os.path.join(paths.actions_dir, txt_file), self.preprocess_data(data)
        )

    def preprocess_data(self, action_groups: dict[int, list[Action]]) -> str:
        output_str = ""
        for at, aa in action_groups.items():
            output_str += f'{at} * len {len(aa)} * ({aa[0].startpos}:{aa[-1].endpos}) \n*{"".join([a.__dict__["content"] for a in aa])}*\n\n'
        return output_str


class TssTxt(Txt):
    def __init__(self, data: list[TransformingSequence]) -> None:
        txt_file = f"{settings.filename}_{Names.TSS}.txt"
        super().__init__(
            os.path.join(paths.tss_dir, txt_file), self.preprocess_data(data)
        )

    def preprocess_data(self, tss: list[TransformingSequence]) -> str:
        output_str = ""
        for ts in tss:
            output_str += f'{ts.label} (pos: {ts.startpos}-{ts.endpos}, dur: {ts.duration}, pause: {ts.preceding_pause}): "{ts.text}"\n\n'
        return output_str


class TpsfsTxt(Txt):
    def __init__(self, data: list[TpsfECM]) -> None:
        txt_file = f"{settings.filename}_{Names.TPSFS}.txt"
        super().__init__(
            os.path.join(paths.tpsfs_dir, txt_file), self.preprocess_data(data)
        )

    def preprocess_data(self, tpsfs: list[TpsfECM]) -> str:
        output_str = ""
        for tpsf in tpsfs:
            tpsf_tus = (
                []
                if not tpsf.textunits
                else [
                    f"({tu_state}) {type(tu).__name__.upper()}:   |{tu.text}|\n"
                    for tu, tu_state in zip(tpsf.textunits, tpsf.tus_states)
                ]
            )
            tus_str = ""
            for ttus in tpsf_tus:
                tus_str += f"{ttus}\n"
            # ts_str = f'The distance between the previous and the current point of inscription: {tpsf.ts_diff}.\n\n'
            # ts_str_no_change = 'Point of inscription unchanged.\n\n'
            # f'{ts_str if tpsf.ts_diff != 0 else ts_str_no_change}' \
            output_str += (
                f"======================{tpsf.revision_id}====================\n\n"
                f"----------------TRANSFORMING SEQUENCE----------------\n\n"
                f"{tpsf.ts.label.upper()} ({tpsf.ts.startpos}-{tpsf.ts.endpos}):\n|{tpsf.ts.text}|\n"
                f"------------------------TEXT-------------------------\n\n"
                f"|{tpsf.text}|\n\n"
                f"----------------------TEXTUNITS----------------------\n\n"
                f"{tus_str}\n"
            )
        return output_str


class TexthisTxt(Txt):
    def __init__(
        self, data: list[TpsfECM], mode: str = "ecm", filtered: bool = False
    ) -> None:
        filter_label = "" if not filtered else "_filtered"
        txt_file = f"{settings.filename}_{Names.TEXTHIS}_{mode}{filter_label}.txt"
        super().__init__(
            os.path.join(paths.texthis_txt_dir, txt_file), self.preprocess_data(data)
        )

    def preprocess_data(self, texthis: list[TpsfECM]) -> str:
        output_str = ""
        for tpsf in texthis:
            output_str += f"{tpsf.to_text()}\n"
        return output_str


class SenhisTxt(Txt):
    def __init__(
        self,
        data: dict[int, list[TextUnit]],
        view_mode: str = "normal",
        filtered: bool = False,
    ) -> None:
        view_mode_name = "" if view_mode == "normal" else f"_{view_mode}"
        filter_label = "" if not filtered else "_filtered"
        txt_file = (
            f"{settings.filename}_{Names.SENHIS}{view_mode_name}{filter_label}.txt"
        )
        super().__init__(
            os.path.join(paths.senhis_txt_dir, txt_file),
            self.preprocess_data(data, view_mode),
        )

    def preprocess_data(self, senhis: dict[int, list[TextUnit]], view_mode: str) -> str:
        output_str = ""
        for id, sens in senhis.items():
            output_str += f"\n******* {id} *******\n"
            for s in sens:
                output_str += f"{s.to_text(view_mode)}\n\n"
        return output_str


class StatsTxt(Txt):
    def __init__(
        self,
        b_stats: BasicStatistics,
        e_stats: EventStatistics,
        p_stats: PauseStatistics,
        ts_stats: TSStatistics,
        sen_stats: SentenceStatistics,
        idfx: str,
    ) -> None:
        txt_file_path = os.path.join(
            paths.stats_dir, settings.filename + "_basic_statistics.txt"
        )
        super().__init__(
            os.path.join(paths.senhis_txt_dir, txt_file_path),
            self.preprocess_data(b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx),
        )

    def preprocess_data(
        self,
        b_stats: BasicStatistics,
        e_stats: EventStatistics,
        p_stats: PauseStatistics,
        ts_stats: TSStatistics,
        sen_stats: SentenceStatistics,
        idfx: str,
    ) -> str:
        source_file = settings.filename + ".idfx"
        task_name = os.path.split(os.path.split(idfx)[0])[-1]
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
            Number text versions in pause capturing mode: {b_stats.data['num_tpsfs_pcm']}

- PAUSES -
            Average pauses duration: {p_stats.data['avg_duration']}
            Maximum pauses duration: {p_stats.data['max_duration']}
            Minimum pauses duration: {p_stats.data['min_duration']}

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
    def __init__(self, data: dict[int, list[list[TokenProp]]], output_dir: str) -> None:
        self.output_dir = output_dir
        self.output = self.preprocess_data(data)

    def preprocess_data(
        self, senhis_parses: dict[int, list[list[TokenProp]]]
    ) -> list[tuple[str, str]]:
        output = []
        for sen_id, sgl_senhis_parses in senhis_parses.items():
            output_path = os.path.join(self.output_dir, f"{sen_id}")
            ensure_path(output_path)
            for senver_id, parsed_sen in enumerate(sgl_senhis_parses):
                output_filepath = os.path.join(output_path, f"{senver_id}.txt")
                output_str = self.generate_str(parsed_sen)
                output.append((output_filepath, output_str))
        return output

    def generate_str(self, parsed_sen: list[TokenProp]) -> str:
        raise NotImplementedError

    def to_file(self) -> None:
        for o in self.output:
            with open(o[0], "w") as f:
                f.write(o[1])


class DepParsesTxt(ParsesTxt):
    def __init__(self, data: dict[int, list[list[TokenProp]]]) -> None:
        super().__init__(data, paths.dependency_senhis_parses_dir)

    def generate_str(self, parsed_sen: list[TokenProp]) -> str:
        output_str = ""
        for tok in parsed_sen:
            output_str += f'{tok["id"]}\t{tok["word"]}\t{tok["pos"]}\t{tok["head"]}\t{tok["dep_rel"]}\n'
        return output_str


class ConstParsesTxt(ParsesTxt):
    def __init__(self, data: dict[int, list[list[TokenProp]]]) -> None:
        super().__init__(data, paths.constituency_senhis_parses_dir)

    def generate_str(self, parsed_sen: list[TokenProp]) -> str:
        return f"{str(parsed_sen)}\n"
