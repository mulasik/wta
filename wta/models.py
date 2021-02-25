import spacy
from spacy.lang.de import German
import benepar


class SpacyModel:
    nlp = German()
    print('Loading Spacy model for German...')
    nlp = spacy.load("de_core_news_md")


# class BeneparModel:
#     benepar.download('benepar_de')
#     parser = benepar.Parser("benepar_de")

