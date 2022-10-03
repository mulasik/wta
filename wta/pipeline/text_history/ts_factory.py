from tqdm import tqdm

from .transforming_sequence import TransformingSequence


class TsFactory:

    @staticmethod
    def run(action_groups):
        tss = []
        action_groups = tqdm(action_groups.items(), 'Extracting transforming sequences')
        for acttyp, actgro in action_groups:
            text = ''.join([a.content for a in actgro])
            actlbl = acttyp.split('_')[0].lower()
            startpos = actgro[0].startpos
            endpos = actgro[-1].endpos
            if actlbl in ['deletion', 'midletion']:
                startpos, endpos = endpos, startpos
            elif actlbl == 'replacement':
                endpos = actgro[-1].rplcmt_endpos
            ts = TransformingSequence(text, actlbl, startpos, endpos)
            tss.append(ts)
        return tss

