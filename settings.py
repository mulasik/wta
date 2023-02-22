from wta.config_data import ConfigData
from wta.language_models.spacy import SpacyModel

config: ConfigData = None  # type: ignore[assignment]
nlp_model: SpacyModel = None  # type: ignore[assignment]
filename: str = None  # type: ignore[assignment]
