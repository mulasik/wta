from pathlib import Path

from ...pipeline.sentence_histories.text_unit import TextUnit
from ...pipeline.sentence_parsing.parsers import TokenProp
from ...pipeline.statistics.statistics import (
    BasicStatistics,
    EventStatistics,
    SentenceStatistics,
    TSStatistics,
)
from ...pipeline.text_history.action import Action
from ...pipeline.text_history.events.base import BaseEvent
from ...pipeline.text_history.tpsf import TpsfECM
from ...pipeline.text_history.ts import TransformingSequence
from ...settings import Settings
from ...utils.other import ensure_path
from .. import names
from .base import BaseStorage


class Txt(BaseStorage):
    def __init__(self, filepath: Path, output_str: str) -> None:
        self.filepath = filepath
        self.output_str = output_str

    def to_file(self) -> None:
        self.filepath.write_text(self.output_str)


class EventsTxt(Txt):
    def __init__(self, data: list[BaseEvent], settings: Settings) -> None:
        txt_file = f"{settings.filename}_{names.EVENTS}.txt"
        super().__init__(
            settings.paths.events_dir / txt_file, self.preprocess_data(data)
        )

    def preprocess_data(self, events: list[BaseEvent]) -> str:
        output_str = ""
        for event in events:
            output_str += f'{type(event).__name__}: *{event.__dict__["content"]}* {event.__dict__["startpos"]} {event.__dict__["endpos"]}\n\n'
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
            output_str += (
                f"{type(a).__name__} ({a.startpos}:{a.endpos}) *{a.content}*\n\n"
            )
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
            output_str += f'{at} * len {len(aa)} * ({aa[0].startpos}:{aa[-1].endpos}) \n*{"".join([a.__dict__["content"] for a in aa])}*\n\n'
        return output_str


class TssTxt(Txt):
    def __init__(self, data: list[TransformingSequence], settings: Settings) -> None:
        txt_file = f"{settings.filename}_{names.TSS}.txt"
        super().__init__(settings.paths.tss_dir / txt_file, self.preprocess_data(data))

    def preprocess_data(self, tss: list[TransformingSequence]) -> str:
        output_str = ""
        for ts in tss:
            output_str += f'{ts.label} (pos: {ts.startpos}-{ts.endpos}, dur: {ts.duration}, pause: {ts.preceding_pause}): "{ts.text}"\n\n'
        return output_str


class TpsfsTxt(Txt):
    def __init__(self, data: list[TpsfECM], settings: Settings) -> None:
        txt_file = f"{settings.filename}_{names.TPSFS}.txt"
        super().__init__(
            settings.paths.tpsfs_dir / txt_file, self.preprocess_data(data)
        )

    def preprocess_data(self, tpsfs: list[TpsfECM]) -> str:
        output_str = ""
        for tpsf in tpsfs:
            tpsf_tus = (
                []
                if not tpsf.textunits
                else [
                    f"({tu.state}) {type(tu).__name__.upper()}:   |{tu.text}|\n"
                    for tu in tpsf.textunits
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
        self,
        data: list[TpsfECM],
        settings: Settings,
        mode: str = "ecm",
        filtered: bool = False,
    ) -> None:
        filter_label = "" if not filtered else "_filtered"
        txt_file = f"{settings.filename}_{names.TEXTHIS}_{mode}{filter_label}.txt"
        super().__init__(
            settings.paths.texthis_txt_dir / txt_file, self.preprocess_data(data)
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

    def preprocess_data(self, senhis: dict[int, list[TextUnit]]) -> str:
        output_str = ""
        for key, sens in senhis.items():
            output_str += f"\n******* {key} *******\n"
            for s in sens:
                output_str += f"{s.to_text()}\n\n"
        return output_str


class StatsTxt(Txt):
    def __init__(
        self,
        b_stats: BasicStatistics,
        e_stats: EventStatistics,
        # p_stats: PauseStatistics,
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
            self.preprocess_data(b_stats, e_stats, ts_stats, sen_stats, idfx, settings),
        )

    def preprocess_data(
        self,
        b_stats: BasicStatistics,
        e_stats: EventStatistics,
        # p_stats: PauseStatistics,
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


# Number text versions in pause capturing mode: {b_stats.data['num_tpsfs_pcm']}
# - PAUSES -
#             Average pauses duration: {p_stats.data['avg_duration']}
#             Maximum pauses duration: {p_stats.data['max_duration']}
#             Minimum pauses duration: {p_stats.data['min_duration']}


class ParsesTxt(Txt):
    def __init__(
        self, data: dict[int, list[list[TokenProp]]], output_dir: Path
    ) -> None:
        self.output_dir = output_dir
        self.output = self.preprocess_data(data)

    def preprocess_data(
        self, senhis_parses: dict[int, list[list[TokenProp]]]
    ) -> list[tuple[Path, str]]:
        output = []
        for sen_id, sgl_senhis_parses in senhis_parses.items():
            output_path = self.output_dir / str(sen_id)
            ensure_path(output_path)
            for senver_id, parsed_sen in enumerate(sgl_senhis_parses):
                output_filepath = output_path / f"{senver_id}.txt"
                output_str = self.generate_str(parsed_sen)
                output.append((output_filepath, output_str))
        return output

    def generate_str(self, parsed_sen: list[TokenProp]) -> str:
        raise NotImplementedError

    def to_file(self) -> None:
        for path, content in self.output:
            path.write_text(content)


class DepParsesTxt(ParsesTxt):
    def __init__(
        self, data: dict[int, list[list[TokenProp]]], settings: Settings
    ) -> None:
        super().__init__(data, settings.paths.dependency_senhis_parses_dir)

    def generate_str(self, parsed_sen: list[TokenProp]) -> str:
        output_str = ""
        for tok in parsed_sen:
            output_str += f'{tok["id"]}\t{tok["word"]}\t{tok["pos"]}\t{tok["head"]}\t{tok["dep_rel"]}\n'
        return output_str


class ConstParsesTxt(ParsesTxt):
    def __init__(
        self, data: dict[int, list[list[TokenProp]]], settings: Settings
    ) -> None:
        super().__init__(data, settings.paths.constituency_senhis_parses_dir)

    def generate_str(self, parsed_sen: list[TokenProp]) -> str:
        return f"{str(parsed_sen)}\n"
