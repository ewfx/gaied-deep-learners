import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List

class Config:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Read configurations with defaults
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
        self.tesseract_path: str = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe").strip()
        self.upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "uploads"))
        self.max_file_size: int = int(os.getenv("MAX_FILE_SIZE", str(25 * 1024 * 1024)))  # Default to 25MB

        # Handle allowed file types safely
        allowed_types = os.getenv("ALLOWED_FILE_TYPES", ".eml,.msg,.pdf,.txt,.csv,.xls,.xlsx")
        self.allowed_file_types: List[str] = [ext.strip().lower() for ext in allowed_types.split(",")]

    def validate(self):
        """ Validates the necessary configurations """
        if not self.gemini_api_key:
            raise ValueError("Error: Gemini API key is required and missing.")

        tesseract_path = Path(self.tesseract_path)
        if not tesseract_path.exists():
            raise FileNotFoundError(f"Error: Tesseract not found at {tesseract_path}")

        # Ensure upload directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)