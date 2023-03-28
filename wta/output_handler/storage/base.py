from abc import ABC, abstractmethod


class BaseStorage(ABC):
    @abstractmethod
    def to_file(self) -> None:
        pass
