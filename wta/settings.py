import dataclasses
from pathlib import Path

from .config_data import ConfigData
from .language_models.spacy import SpacyModel
from .output_handler import names
from .utils.other import ensure_path


@dataclasses.dataclass(frozen=True)
class Paths:
    events_dir: Path
    actions_dir: Path
    tss_dir: Path
    tpsfs_dir: Path
    texthis_json_dir: Path
    texthis_txt_dir: Path
    texthis_visual_dir: Path
    stats_dir: Path
    senhis_json_dir: Path
    senhis_txt_dir: Path
    senhood_json_dir: Path
    senhood_txt_dir: Path
    senhis_visual_dir: Path
    dependency_senhis_parses_dir: Path
    constituency_senhis_parses_dir: Path
    transhis_dir: Path
    dependency_transhis_dir: Path
    constituency_transhis_dir: Path


@dataclasses.dataclass(frozen=True)
class Settings:
    config: ConfigData
    nlp_model: SpacyModel
    filename: str
    _paths: Paths | None = None

    @property
    def paths(self) -> Paths:
        if self._paths is not None:
            return self._paths
        paths = _create_paths(self.config["output_dir"])
        object.__setattr__(self, "_paths", paths)
        return paths


def _create_paths(output_dir: Path) -> Paths:
    preprocessing_dir = output_dir / names.PREPROCESSING
    texthis_dir = output_dir / names.TEXTHIS
    transhis_dir = output_dir / names.TRANSHIS
    senhis_dir = output_dir / names.SENHIS
    senhood_dir = output_dir / names.SENHOOD
    senhis_parses_dir = senhis_dir / names.SENPAR

    paths = Paths(
        events_dir=preprocessing_dir / names.EVENTS,
        actions_dir=preprocessing_dir / names.ACTIONS,
        tss_dir=preprocessing_dir / names.TSS,
        tpsfs_dir=preprocessing_dir / names.TPSFS,
        texthis_json_dir=texthis_dir / names.JSON,
        texthis_txt_dir=texthis_dir / names.TXT,
        texthis_visual_dir=texthis_dir / names.VISUAL,
        stats_dir=output_dir / names.STATS,
        senhis_json_dir=senhis_dir / names.JSON,
        senhis_txt_dir=senhis_dir / names.TXT,
        senhood_json_dir=senhood_dir / names.JSON,
        senhood_txt_dir=senhood_dir / names.TXT,
        senhis_visual_dir=senhis_dir / names.VISUAL,
        dependency_senhis_parses_dir=senhis_parses_dir / names.DEP,
        constituency_senhis_parses_dir=senhis_parses_dir / names.CONST,
        transhis_dir=transhis_dir,
        dependency_transhis_dir=transhis_dir / names.DEP,
        constituency_transhis_dir=transhis_dir / names.CONST,
    )

    paths_to_ensure = [d for d in dir(paths) if d.endswith("_dir")]
    for p in paths_to_ensure:
        ensure_path(getattr(paths, p))

    return paths
