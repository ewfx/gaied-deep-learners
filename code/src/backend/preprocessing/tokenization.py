import spacy
from typing import List

class EmailTokenizer:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise ImportError("English language model for spaCy not found. Run 'python -m spacy download en_core_web_sm'")

    def tokenize_email(self, text: str) -> List[str]:
        """Convert email text into meaningful tokens"""
        doc = self.nlp(text)
        return [token.lemma_.lower() for token in doc 
                if not token.is_stop and not token.is_punct and token.is_alpha]