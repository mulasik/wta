from typing import Literal

from nltk.tokenize.api import TokenizerI

def load(
    resource_url: str,
    format: Literal[
        "auto",
        "pickle",
        "json",
        "yaml",
        "cfg",
        "pcfg",
        "fcfg",
        "fol",
        "logic",
        "val",
        "text",
        "raw",
    ] = ...,
    cache: bool = ...,
    verbose: bool = ...,
    encoding: str = ...,
) -> TokenizerI: ...
