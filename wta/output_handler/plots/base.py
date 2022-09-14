from abc import ABC, abstractmethod


class BasePlot(ABC):

    @abstractmethod
    def preprocess_data(self):
        pass

    @abstractmethod
    def create_figure(self):
        pass

    @abstractmethod
    def plot_data(self):
        pass

    @abstractmethod
    def set_legend(self):
        pass

    @abstractmethod
    def run(self):
        pass

