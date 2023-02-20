import os

import paths
import settings
from wta.output_handler.names import Names
from wta.utils.other import ensure_path
from .storage.json import TexthisJson, SenhisJson, TranshisJson
from .storage.txt import EventsTxt, ActionsTxt, ActionGroupsTxt, TssTxt, TpsfsTxt, TexthisTxt, SenhisTxt, StatsTxt, DepParsesTxt, ConstParsesTxt
from .storage.svg import (TexthisSvg, FilteredTexthisSvg,
                          SenhisSvg,
                          DepTranshisSvg, ConstTranshisSvg, SynBarTranshisSvg, SynPieTranshisSvg,
                          SenEditSvg, TsLabelsSvg, TsTokensSvg, DeletionsSvg, InsertionsSvg)


class StorageSettings:

    @classmethod
    def set_paths(cls):
        paths.events_dir = os.path.join(settings.config['output_dir'], Names.PREPROCESSING, Names.EVENTS)
        paths.actions_dir = os.path.join(settings.config['output_dir'], Names.PREPROCESSING, Names.ACTIONS)
        paths.tss_dir = os.path.join(settings.config['output_dir'], Names.PREPROCESSING, Names.TSS)
        paths.tpsfs_dir = os.path.join(settings.config['output_dir'], Names.PREPROCESSING, Names.TPSFS)
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
        paths.transhis_dir = os.path.join(settings.config['output_dir'], Names.TRANSHIS)
        paths.dependency_transhis_dir = os.path.join(paths.transhis_dir, Names.DEP)
        paths.constituency_transhis_dir = os.path.join(paths.transhis_dir, Names.CONST)
        paths_to_ensure = [d for d in dir(paths) if d.endswith('_dir')]
        for p in paths_to_ensure:
            ensure_path(getattr(paths, p))


class OutputFactory:

    @classmethod
    def run(cls):
        raise NotImplementedError


class EventsOutputFactory(OutputFactory):

    @classmethod
    def run(cls, events):
        StorageSettings.set_paths()
        EventsTxt(events).to_file()


class ActionsOutputFactory(OutputFactory):

    @classmethod
    def run(cls, actions):
        StorageSettings.set_paths()
        ActionsTxt(actions).to_file()


class ActionGroupsOutputFactory(OutputFactory):

    @classmethod
    def run(cls, action_groups):
        StorageSettings.set_paths()
        ActionGroupsTxt(action_groups).to_file()


class TssOutputFactory(OutputFactory):

    @classmethod
    def run(cls, tss):
        StorageSettings.set_paths()
        TssTxt(tss).to_file()


class TpsfsOutputFactory(OutputFactory):

    @classmethod
    def run(cls, tpsfs):
        StorageSettings.set_paths()
        TpsfsTxt(tpsfs).to_file()


class TexthisOutputFactory(OutputFactory):

    @classmethod
    def run(cls, texthis):  # + texthis_pcm
        StorageSettings.set_paths()
        TexthisJson(texthis).to_file()
        # TODO: TexthisJson(texthis_pcm, mode='pcm').to_file()
        TexthisTxt(texthis).to_file()
        TexthisSvg(texthis).to_file()


class TexthisFltrOutputFactory(OutputFactory):

    @classmethod
    def run(cls, texthis_fltr):  # + texthis_pcm
        StorageSettings.set_paths()
        TexthisJson(texthis_fltr, filtered=True).to_file()
        TexthisTxt(texthis_fltr, filtered=True).to_file()
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
        DepTranshisSvg(dep_transhis).to_file()
        ConstTranshisSvg(const_transhis).to_file()
        SynBarTranshisSvg(dep_transhis, const_transhis).to_file()
        SynPieTranshisSvg(dep_transhis, const_transhis).to_file()


class StatsOutputFactory(OutputFactory):

    @classmethod
    def run(cls, b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx, texthis, senhis):
        StorageSettings.set_paths()
        StatsTxt(b_stats, e_stats, p_stats, ts_stats, sen_stats, idfx).to_file()
        SenEditSvg(texthis, senhis).to_file()
        TsTokensSvg(texthis, senhis).to_file()
        TsLabelsSvg(texthis, senhis).to_file()
        DeletionsSvg(texthis, senhis).to_file()
        InsertionsSvg(texthis, senhis).to_file()

