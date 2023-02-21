from abc import ABC, abstractmethod


class BaseStorage(ABC):
    @abstractmethod
    def preprocess_data(self):
        pass

    @abstractmethod
    def to_file(self):
        pass
