from collections.abc import Iterable, Iterator

from .transform import Sentence

class Dataset(Iterable[Sentence]):
    def __iter__(self) -> Iterator[Sentence]: ...
