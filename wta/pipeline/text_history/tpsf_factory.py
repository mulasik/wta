from tqdm import tqdm


class TpsfFactory:
    """
    A class to retrieve text versions based on transforming sequences (TSs).
    There are 4 types of TSs where text is produced:
    - append
    - insertion
    - pasting
    There are 2 types of TSs where text is deleted:
    - deletion
    - midletion
    There is 1 type of TSs where text is deleted and produced at the same time:
    - replacement
    There is 1 type of TSs where no changes to text are made:
    - navigation
    """

    @staticmethod
    def run(tss):
        output = []
        tpsfs = []
        tss = [ts for ts in tss if ts.label != 'navigation']
        tss = tqdm(tss, 'Extracting tpsfs')
        for ts in tss:
            # print(ts.label)
            if ts.label in ['append', 'insertion', 'pasting']:
                startpos = ts.startpos
                for char in ts.text:
                    # print(f'Will insert *{char}* at {startpos}')
                    output.insert(startpos, char)
                    startpos += 1
                # print(len(output), 'POS:', ts.startpos, ts.endpos)
            elif ts.label in ['deletion', 'midletion']:
                text = output[ts.startpos:ts.endpos + 1]
                ts.set_text(text)
                # print(f'Will remove *{output[ts.startpos:ts.endpos + 1]}* at {ts.startpos}-{ts.endpos}')
                del output[ts.startpos:ts.endpos + 1]
                # print(len(output), 'POS:', ts.startpos, ts.endpos)
            elif ts.label == 'replacement':
                # print(f'Will remove *{output[ts.startpos:ts.endpos + 1]}* at {ts.startpos}-{ts.endpos}')
                del output[ts.startpos:ts.endpos + 1]
                startpos = ts.startpos
                for char in ts.text:
                    output.insert(startpos, char)
                    startpos += 1
                # print(len(output), 'POS:', ts.startpos, ts.endpos)
            tpsfs.append((ts.text, ts.startpos, ts.endpos, ts.label, "".join(output)))
            # print(f'*{"".join(output)}*')
        # print('FINAL OUTPUT')
        # print(f'*{"".join(output)}*')
        return tss, tpsfs

