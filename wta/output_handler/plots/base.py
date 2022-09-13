import settings


class BasePlot:

    def __init__(self, data, filtered=False):
        self.output_directory = settings.config['output_dir']
        self.filename = settings.filename
        self.filtered = '' if not filtered else '_filtered'
        self.data = self.preprocess_data(data)

    def preprocess_data(self):
        pass

    def plot_data(self):
        pass

