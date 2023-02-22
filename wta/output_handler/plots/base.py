from abc import ABC, abstractmethod


class BasePlot(ABC):
    @abstractmethod
    def run(self) -> None:
        pass
