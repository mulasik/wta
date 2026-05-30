from wta.pipeline.BL2TL_projection.burst import Burst


class BurstFactory:

    def run(
            self,
            text: str,
            pauses: list[float]|None,
            ts_following_pause: float|None,
            tpsf_id: int|None,
            ts_label: str
            ) -> list[Burst]:
        bursts = []
        if pauses is not None and len(pauses) > 0:
            preceding_pause = pauses[0]
            burst_text = ""
            initial_pause = preceding_pause
            for p, ch in zip(pauses, text):
                if p is None or p <= 2:
                    burst_text += ch
                elif p is not None and p > 2 and len(burst_text) > 0:
                    following_pause = p
                    burst = Burst(initial_pause, following_pause, burst_text, tpsf_id, ts_label)
                    bursts.append(burst)
                    initial_pause = p
                    burst_text = ch
            bursts.append(Burst(initial_pause, ts_following_pause, burst_text, tpsf_id, ts_label))
        elif pauses is None or len(pauses) == 0:
            burst = Burst(None, None, "", tpsf_id, ts_label)
            bursts.append(burst)

        # else:
        #     print(f"INFO: No pause data available for the TS |{text}|. Could not extract bursts.")
        return bursts
