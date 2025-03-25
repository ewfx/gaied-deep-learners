import os
from dotenv import load_dotenv
from pathlib import Path

class Config:
    def __init__(self):
        load_dotenv()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.tesseract_path = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    def validate(self):
        if not self.gemini_api_key:
            raise ValueError("Gemini API key is required")
        if not Path(self.tesseract_path).exists():
            raise FileNotFoundError(f"Tesseract not found at {self.tesseract_path}")