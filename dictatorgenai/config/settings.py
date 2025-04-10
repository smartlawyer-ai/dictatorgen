from dictatorgenai.models.base_model import BaseModel


class DictatorSettings():
    """
    Centralized configuration settings for the Dictator Framework.
    """
    language: str = "en"  # Default language for responses
    confidence_threshold: float = 0.7  # Confidence threshold for general selection
    logging_level: str = "INFO"  # Default logging level 
    nlp_model: BaseModel = None  # Default NLP model for task analysis

    @classmethod
    def set_language(cls, language: str):
        """
        Change the default language for the framework.
        """
        cls.language = language

    @classmethod
    def get_language(cls):
        """
        Retrieve the current default language.
        """
        return cls.language
    
    @classmethod
    def set_nlp_model(cls, nlp_model: BaseModel):
        """
        Change the default language for the framework.
        """
        cls.nlp_model = nlp_model

    @classmethod
    def get_nlp_model(cls):
        """
        Retrieve the current default language.
        """
        return cls.nlp_model
