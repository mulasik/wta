from tqdm import tqdm

from .tpsf import TpsfECM


class TpsfFactory:
    def run(self):
        pass


class ECMFactory(TpsfFactory):
    """
    A class to retrieve text versions (TPSFs) in Edit Capturing Mode (ECM).
    TPSFs are generated based on transforming sequences (TSs).
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
        """
        Generates a list of objects of type Tpsf based on a list of transforming sequences.
        Args:
            tss: a list of objects of type TransformingSequence
        Returns:
            a list of objects of type Tpsf
        """
        output = []
        tpsfs = []
        tss = [ts for ts in tss if ts.label != "navigation"]
        tss = tqdm(tss, "Extracting tpsfs")
        prev_tpsf = None
        for i, ts in enumerate(tss):
            if ts.label in ["append", "insertion", "pasting"]:
                startpos = ts.startpos
                for char in ts.text:
                    output.insert(startpos, char)
                    startpos += 1
            elif ts.label in ["deletion", "midletion"]:
                text = output[ts.startpos : ts.endpos + 1]
                ts.set_text("".join(text))
                del output[ts.startpos : ts.endpos + 1]
            elif ts.label == "replacement":
                del output[ts.startpos : ts.endpos + 1]
                startpos = ts.startpos
                for char in ts.text:
                    output.insert(startpos, char)
                    startpos += 1
            content = "".join(output)
            tpsf = TpsfECM(i, content, ts, prev_tpsf)
            tpsfs.append(tpsf)
            prev_tpsf = tpsf
        return tpsfs