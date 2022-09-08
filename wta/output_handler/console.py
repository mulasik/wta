import json


class Console:

    def __init__(self, texthis: dict, senhis: dict, mode: str, filtered: bool):
        self.texthis = texthis
        self.senhis = senhis
        self.mode = mode
        self.filtered = filtered

    def texthis_to_console(self):
        _texthis = []
        for tpsf in self.texthis:
            _texthis.append(tpsf.to_dict())
        print(json.dumps(_texthis, indent=5))

    def senhis_to_console(self):
        _senhis = {}
        for id, sens in self.senhis.items():
            _senhis[id] = [s.to_dict() for s in sens]
        print(json.dumps(_senhis, indent=5))

    def revnum_to_console(self):
        _filtered = 'filtered' if self.filtered is True else 'all'
        print(f'{self.mode}: {len(self.texthis)} text revisions ({_filtered}).')

