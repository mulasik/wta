from wta.pipeline.BL2TL_projection.burst import Burst
from wta.pipeline.transformation_layer.tpsf import Tpsf


class BursthisGenerator:

    def run(self, tpsfs: list[Tpsf]) -> list[Burst]:
        burst_list = []
        for tpsf in tpsfs:
            for b in tpsf.ts.bursts:
                b.set_tpsf_id(tpsf.id)
                burst_list.append(b)
        return burst_list

