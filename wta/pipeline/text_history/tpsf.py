from ..sentence_histories.text_unit_factory import TextUnitFactory


class TpsfECM:

    def __init__(self, revision_id, content, ts, prev_tpsf, final=False):
        self.revision_id = revision_id
        self.text = content
        self.ts = ts
        self.prev_tpsf = prev_tpsf
        self.final = final
        self.textunits, self.tus_states = TextUnitFactory().run(self.text, self.revision_id, self.ts, self.prev_tpsf)

    def __str__(self):
        return f'''

=== TPSF ===

PREVIOUS TEXT:  
{self.prev_text_version}

RESULT TEXT:            
{self.result_text}

TRANSFORMING SEQUENCE: 
{self.ts.label.upper()} *{self.ts.text}*

            '''

    def to_dict(self):
        tpsf_dict = {
            "revision_id": self.revision_id,
            "prev_text_version": None if not self.prev_tpsf else self.prev_tpsf.text,
            "result_text": self.text,
            "edit": {
                "transforming_sequence": self.ts.__dict__,
            },
            "textunits": {
                "previous_textunits": [] if not self.prev_tpsf else [tu.to_dict() for tu in self.prev_tpsf.textunits],
                "current_textunits": [tu.to_dict() for tu in self.textunits],
            },
        }
        return tpsf_dict

    def to_text(self):
        return f"""
TPSF version {self.revision_id}:
{self.text}
TS: 
{(self.ts.text, self.ts.label.upper())}
            """
