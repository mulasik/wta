import os

import paths
import settings
from wta.output_handler.names import Names
from wta.utils.other import ensure_path
from wta.output_handler.storage.json import TexthisJson, SenhisJson, TranshisJson
from wta.output_handler.storage.txt import TexthisTxt, SenhisTxt, StatsTxt, DepParsesTxt, ConstParsesTxt
from wta.output_handler.storage.svg import TexthisSvg, FilteredTexthisSvg, SenhisSvg
from wta.output_handler.plots.transhis_plot import TranshisPlot
from wta.output_handler.plots.stats_plot import StatsPlot


class StorageSettings:

    @classmethod
    def set_paths(cls):
        paths.texthis_dir = os.path.join(settings.config['output_dir'], Names.TEXTHIS)
        paths.texthis_json_dir = os.path.join(paths.texthis_dir, Names.JSON)
        paths.texthis_txt_dir = os.path.join(paths.texthis_dir, Names.TXT)
        paths.texthis_visual_dir = os.path.join(paths.texthis_dir, Names.VISUAL)
        paths.stats_dir = os.path.join(settings.config['output_dir'], Names.STATS)
        paths.senhis_dir = os.path.join(settings.config['output_dir'], Names.SENHIS)
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


class OutputFactory:

    @classmethod
    def run(cls):
        raise NotImplementedError


class TexthisOutputFactory(OutputFactory):

    @classmethod
    def run(cls, texthis, texthis_pcm, texthis_fltr):
        StorageSettings.set_paths()
        TexthisJson(texthis).to_file()
        TexthisJson(texthis_pcm, mode='pcm').to_file()
        TexthisJson(texthis_fltr, filtered=True).to_file()
        TexthisTxt(texthis).to_file()
        TexthisTxt(texthis_fltr, filtered=True).to_file()
        TexthisSvg(texthis).to_file()
        FilteredTexthisSvg(texthis_fltr).to_file()


class SenhisOutputFactory(OutputFactory):

    @classmethod
    def run(cls, texthis, texthis_fltr, senhis, senhis_fltr):
        StorageSettings.set_paths()
        SenhisJson(senhis).to_file()
        SenhisJson(senhis, 'simplified').to_file()
        SenhisJson(senhis_fltr, filtered=True).to_file()
        SenhisJson(senhis_fltr, 'simplified', filtered=True).to_file()
        SenhisTxt(senhis).to_file()
        SenhisTxt(senhis_fltr, filtered=True).to_file()
        SenhisTxt(senhis, view_mode='extended').to_file()
        SenhisTxt(senhis, view_mode='extended', filtered=True).to_file()
        SenhisSvg(texthis, senhis).to_file()
        SenhisSvg(texthis_fltr, senhis_fltr, filtered=True).to_file()


class ParseOutputFactory(OutputFactory):

    @classmethod
    def run(cls, dep_senhis_parses, const_senhis_parses):
        DepParsesTxt(dep_senhis_parses).to_file()
        ConstParsesTxt(const_senhis_parses).to_file()


class TranshisOutputFactory(OutputFactory):

    @classmethod
    def run(cls, dep_transhis, const_transhis):
        TranshisJson(dep_transhis, 'dependency').to_file()
        TranshisJson(const_transhis, 'constituency').to_file()
        TranshisPlot().plot_data()


class StatsOutputFactory(OutputFactory):

    @classmethod
    def run(cls, b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx, texthis, senhis):
        StorageSettings.set_paths()
        StatsTxt(b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx).to_file()
        StatsPlot().plot_data(texthis, senhis)

