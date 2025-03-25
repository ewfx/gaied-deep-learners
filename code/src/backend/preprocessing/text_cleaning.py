import re
from typing import Optional

class EmailCleaner:
    @staticmethod
    def remove_signatures(text: str) -> str:
        # Remove common email signature patterns
        patterns = [
            r'(?s)(--\s*[\r\n]|__[\r\n]).*$',  # Signature after -- or __
            r'(?i)(best regards|kind regards|thanks|cheers)[\s\S]*$',
            r'(?m)^sent from my (iphone|android).*$'
        ]
        for pattern in patterns:
            text = re.sub(pattern, '', text)
        return text.strip()

    @staticmethod
    def remove_disclaimers(text: str) -> str:
        # Remove legal disclaimers
        disclaimer_patterns = [
            r'(?s)confidentiality notice.*$',
            r'(?s)this message is confidential.*$'
        ]
        for pattern in disclaimer_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text

    def clean_email_content(self, email_body: str) -> str:
        if not email_body:
            return ""
        
        cleaned = self.remove_signatures(email_body)
        cleaned = self.remove_disclaimers(cleaned)
        
        # Remove multiple empty lines
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        
        return cleaned.strip()