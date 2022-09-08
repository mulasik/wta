from wta.output_handler.storage.base import BaseStorage, TranshisStorage, StatsStorage


class Svg(BaseStorage, TranshisStorage, StatsStorage):

    def process_texthis(self, tpsfs: list, mode: str, filtered=False):
        ...

    def process_senhis(self, sen_hist: dict, view_mode='normal', filtered=False):
        ...

    def process_transhis(self, transhis: dict, grammar: str):
        ...

    def process_stats(self):
        ...