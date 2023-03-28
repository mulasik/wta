from collections.abc import Iterable, Iterator

class Dataset(Iterable[str]):
    def __iter__(self) -> Iterator[str]: ...
