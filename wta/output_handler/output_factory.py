import os

import paths
import settings
from wta.output_handler.storage.names import Names
from wta.utils.other import ensure_path
from wta.output_handler.storage.json import TexthisJson, SenhisJson, TranshisJson
from wta.output_handler.storage.txt import TexthisTxt, SenhisTxt, StatsTxt, DepParsesTxt, ConstParsesTxt
from wta.output_handler.storage.svg import TexthisSvg, SenhisSvg
from wta.output_handler.plots.texthis_plot import TexthisPlot, FilteredTexthisPlot
from wta.output_handler.plots.senhis_plot import SenhisPlot
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
        TexthisJson(texthis).to_json()
        TexthisJson(texthis_pcm, mode='pcm').to_json()
        TexthisJson(texthis_fltr, filtered=True).to_json()
        TexthisTxt(texthis).to_txt()
        TexthisTxt(texthis_fltr, filtered=True).to_txt()
        texthis_plot = TexthisPlot(texthis).plot_data()
        fltr_texthis_plot = FilteredTexthisPlot(texthis_fltr).plot_data()
        TexthisSvg(texthis_plot).to_svg()
        TexthisSvg(fltr_texthis_plot, filtered=True).to_svg()


class SenhisOutputFactory(OutputFactory):

    @classmethod
    def run(cls, texthis, texthis_fltr, senhis, senhis_fltr):
        StorageSettings.set_paths()
        SenhisJson(senhis).to_json()
        SenhisJson(senhis, 'simplified').to_json()
        SenhisJson(senhis_fltr, filtered=True).to_json()
        SenhisJson(senhis_fltr, 'simplified', filtered=True).to_json()
        SenhisTxt(senhis).to_txt()
        SenhisTxt(senhis_fltr, filtered=True).to_txt()
        SenhisTxt(senhis, view_mode='extended').to_txt()
        SenhisTxt(senhis, view_mode='extended', filtered=True).to_txt()
        senhis_plot = SenhisPlot(texthis, senhis).plot_data()
        fltr_senhis_plot = SenhisPlot(texthis_fltr, senhis_fltr).plot_data()
        SenhisSvg(senhis_plot).to_svg()
        SenhisSvg(fltr_senhis_plot, filtered=True).to_svg()


class ParseOutputFactory(OutputFactory):

    @classmethod
    def run(cls, dep_senhis_parses, const_senhis_parses):
        DepParsesTxt(dep_senhis_parses).to_txt()
        ConstParsesTxt(const_senhis_parses).to_txt()


class TranshisOutputFactory(OutputFactory):

    @classmethod
    def run(cls, dep_transhis, const_transhis):
        TranshisJson(dep_transhis, 'dependency').to_json()
        TranshisJson(const_transhis, 'constituency').to_json()
        TranshisPlot().plot_data()


class StatsOutputFactory(OutputFactory):

    @classmethod
    def run(cls, b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx, texthis, senhis):
        StorageSettings.set_paths()
        StatsTxt(b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx).to_txt()
        StatsPlot().plot_data(texthis, senhis)
