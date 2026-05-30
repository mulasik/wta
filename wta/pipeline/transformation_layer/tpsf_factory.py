from tqdm import tqdm

from wta.pipeline.names import TSLabels, TUState
from wta.pipeline.SL2TL_projection.sl2tl_projector import SL2TLProjector
from wta.pipeline.SL2TL_projection.textunit import Textunit

from ...settings import Settings
from .tpsf import Tpsf
from .ts import TransformingSequence, TSBuilder


class TpsfFactory:
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
    def run(tsbs: list[TSBuilder], settings: Settings) -> list[Tpsf]:
        """
        Generates a list of objects of type Tpsf based on a list of transforming sequences.
        Args:
            tss: a list of objects of type TransformingSequence
        Returns:
            a list of objects of type TpsfECM
        """
        tpsfs: list[Tpsf] = []
        aggregated_tss: tuple[TransformingSequence, ...] = ()
        output: list[str] = []
        tsbs = [ts for ts in tsbs if ts.label != "navigation"]
        prev_tpsf = None

        # exctract tpsfs based on tss
        for i, tsb in enumerate(tqdm(tsbs, "Extracting tpsfs")):

            # extract tpsf content
            output, removed_text = _extract_tpsf_text(tsb, output)
            tpsf_text = "".join(output)
            if tsb.label in [TSLabels.DEL, TSLabels.MID]:
                ts_text = removed_text
                ts_replaced_text = ""
            elif tsb.label == TSLabels.REPL:
                ts_text = tsb.text
                ts_replaced_text = removed_text
            else:
                ts_text = tsb.text
                ts_replaced_text = ""

            # collect data from the projection of sentence layer on transforming layer
            sen_trans_prjctr = SL2TLProjector(i, tpsf_text, tsb, prev_tpsf, removed_text, ts_text, settings)

            # after having collected all required data,
            # transform data collectors into fully propagated TS and TextUnits
            # (TS and TextUnits are objects of frozen dataclasses)
            ts = tsb.to_transforming_sequence(ts_text, ts_replaced_text, sen_trans_prjctr.sscope, sen_trans_prjctr.tssegments, sen_trans_prjctr.replaced_segments, settings)
            tus_current = [tu.to_text_unit() for tu in sen_trans_prjctr.tubs_current]
            deleted_tus = [tu.to_text_unit() for tu in sen_trans_prjctr.deleted_tubs]

            # evaluate TPSF relevance
            relevance = _determine_tpsf_relevance(ts, tus_current, settings)
            aggregated_tss = () if relevance else (*aggregated_tss, ts)

            # create TPSF
            tpsf = Tpsf(i, tpsf_text, ts, prev_tpsf, tus_current, deleted_tus, relevance, aggregated_tss)

            # append TPSF to the text history
            tpsfs.append(tpsf)

            prev_tpsf = tpsf

        return tpsfs

def _extract_tpsf_text(tsb: TSBuilder, output: list[str]) -> tuple[list[str], str]:
    after_end_pos = -1 if tsb.endpos is None else tsb.endpos + 1
    # print(f"LABEL: {tsb.label}, startpos: {tsb.startpos}, endpos: {tsb.endpos}, after_end_pos: {after_end_pos}, text: {tsb.text}, repl textlen: {tsb.rplcmt_textlen}")
    # print(f"tsb.startpos : after_end_pos = {tsb.startpos} : {after_end_pos}")
    if tsb.label in [TSLabels.APP, TSLabels.INS, TSLabels.PAST]:
                startpos = tsb.startpos
                for char in tsb.text:
                    output.insert(startpos, char)
                    startpos += 1
                removed_text = ""
                # print(f"TPSF text: {''.join(output)}, removed text: {removed_text}")
    elif tsb.label in [TSLabels.DEL, TSLabels.MID]:
                text = output[tsb.startpos : after_end_pos]
                removed_text = "".join(text)
                del output[tsb.startpos : after_end_pos]
                # print(f"TPSF text as result of deletion: {''.join(output)}, removed text: {removed_text}")
    elif tsb.label == TSLabels.REPL and tsb.startpos is not None and tsb.rplcmt_textlen > -1:
                after_end_pos = tsb.startpos + tsb.rplcmt_textlen
                removed_text = "".join(output[tsb.startpos : after_end_pos])
                del output[tsb.startpos : after_end_pos]
                startpos = tsb.startpos
                for char in tsb.text:
                    output.insert(startpos, char)
                    startpos += 1
                # print(f"TPSF text: {''.join(output)}, removed text: {removed_text}")
    else:
        print(f"WARNING: Unable to extract TPSF text for TS {tsb.label}, {tsb.startpos}, {tsb.rplcmt_textlen}.")
    return output, removed_text





def _determine_tpsf_relevance(ts: TransformingSequence, textunits: list[Textunit], settings: Settings) -> bool:
    if settings.config["enable_spellchecking"] is False:
        return ts.relevance
    impacted_tus = [tu for tu in textunits if tu.state in [TUState.NEW, TUState.MOD]]
    for itu in impacted_tus:
        tagged_tokens = [] if itu.text is None or itu.text == "" else settings.nlp_model.tag_words(itu.text)
        if True in [t["is_typo"] for t in tagged_tokens]:
            return False
    return True

def filter_tpsfs(tpsfs: list[Tpsf]) -> list[Tpsf]:
    return [tpsf for tpsf in tpsfs if tpsf.relevance is True]
