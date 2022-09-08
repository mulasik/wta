import os
from abc import ABC, abstractmethod

import settings
import paths
from wta.utils.other import ensure_path


class Names:

    TEXTHIS = 'text_history'
    JSON = 'json'
    TXT = 'txt'
    STATS = 'statistics'
    SENHIS = 'sentence_histories'
    SENPAR = 'sentence_parses'
    TRANSHIS = 'transformation_histories'
    DEP = 'dependency'
    CONST = 'constituency'
    VISUAL = 'visualisations'


class StorageSettings:

    @classmethod
    def set_paths(self):
        paths.texthis_dir = os.path.join(settings.config['output_handler'], Names.TEXTHIS)
        paths.texthis_json_dir = os.path.join(paths.texthis_dir, Names.JSON)
        paths.texthis_txt_dir = os.path.join(paths.texthis_dir, Names.TXT)
        paths.texthis_visual_dir = os.path.join(paths.texthis_dir, Names.VISUAL)
        paths.stats_dir = os.path.join(settings.config['output_handler'], Names.STATS)
        paths.senhis_dir = os.path.join(settings.config['output_handler'], Names.SENHIS)
        paths.senhis_json_dir = os.path.join(paths.senhis_dir, Names.JSON)
        paths.senhis_txt_dir = os.path.join(paths.senhis_dir, Names.TXT)
        paths.senhis_visual_dir = os.path.join(paths.senhis_dir, Names.VISUAL)
        paths.senhis_parses_dir = os.path.join(paths.senhis_dir, Names.SENPAR)
        paths.dependency_senhis_parses_dir = os.path.join(paths.senhis_parses_dir, Names.DEP)
        paths.constituency_senhis_parses_dir = os.path.join(paths.senhis_parses_dir, Names.CONST)
        paths.transhis_dir = os.path.join(paths.senhis_dir, Names.TRANSHIS)
        paths.dependency_transhis_dir = os.path.join(paths.transhis_dir, Names.DEP)
        paths.constituency_transhis_dir = os.path.join(paths.transhis_dir, Names.CONST)
        paths_to_ensure = [d for d in dir(paths) if d.endswith('_dir')]
        for p in paths_to_ensure:
            ensure_path(getattr(paths, p))


class BaseStorage(ABC):

    @abstractmethod
    def process_texthis(self, tpsfs: list, mode: str, filtered=False):
        pass

    @abstractmethod
    def process_senhis(self, sen_hist: dict, view_mode='normal', filtered=False):
        pass


class ParsesStorage(ABC):

    @abstractmethod
    def process_dependency_parses(self, senhis_parses: dict, output_path: str):
        pass

    @abstractmethod
    def process_constituency_parses(self, senhis_parses: dict, output_path: str):
        pass


class TranshisStorage(ABC):

    @abstractmethod
    def process_transhis(self, transhis: dict, grammar: str):
        pass


class StatsStorage(ABC):

    @abstractmethod
    def process_stats(self):
        pass

