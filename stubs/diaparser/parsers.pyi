from .utils import Dataset

class Parser:
    @classmethod
    def load(
        cls, name_or_path: str = ..., lang: str = ..., cache_dir: str = ...
    ) -> Parser: ...
    def predict(
        self,
        data: str | list[list[str]],
        pred: str = ...,
        buckets: int = ...,
        batch_size: int = ...,
        prob: bool = ...,
        *,
        text: str = ...
    ) -> Dataset: ...
