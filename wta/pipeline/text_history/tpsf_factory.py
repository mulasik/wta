from tqdm import tqdm

from ...settings import Settings
from .tpsf import TpsfECM
from .ts import TransformingSequence


class ECMFactory:
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
    def run(tss: list[TransformingSequence], settings: Settings) -> list[TpsfECM]:
        """
        Generates a list of objects of type Tpsf based on a list of transforming sequences.
        Args:
            tss: a list of objects of type TransformingSequence
        Returns:
            a list of objects of type Tpsf
        """
        output: list[str] = []
        tpsfs = []
        tss = [ts for ts in tss if ts.label != "navigation"]
        prev_tpsf = None
        for i, ts in enumerate(tqdm(tss, "Extracting tpsfs")):
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
            tpsf = TpsfECM(i, content, ts, prev_tpsf, settings)
            tpsfs.append(tpsf)
            prev_tpsf = tpsf
        return tpsfs
