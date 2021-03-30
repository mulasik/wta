class SpacyModel:

    def __init__(self, lang):
        import spacy
        if lang == 'German':
            import spacy
            from spacy.lang.de import German
            self.nlp = German()
            print('Loading Spacy model for German...')
            self.nlp = spacy.load("de_core_news_md")
        elif lang == 'English':
            from spacy.lang.en import English
            self.nlp = English()
            print('Loading Spacy model for English...')
            self.nlp = spacy.load("en_core_web_md")


class BeneparModel:

    def __init__(self, lang):
        if lang == 'German':
            import benepar
            benepar.download('benepar_de')
            self.parser = benepar.Parser("benepar_de")


