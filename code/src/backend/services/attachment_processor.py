import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import pandas as pd
import os

class AttachmentProcessor:
    def __init__(self, tesseract_path: str):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def extract_text(self, file_path: str) -> str:
        """Extracts text from PDFs, images, CSVs, and Excel files."""
        try:
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                return pytesseract.image_to_string(file_path)
            elif file_path.lower().endswith('.pdf'):
                with open(file_path, 'rb') as f:
                    reader = PdfReader(f)
                    text = "\n".join([page.extract_text() or "" for page in reader.pages])
                    if text.strip():
                        return text
                images = convert_from_path(file_path)
                return "\n".join([pytesseract.image_to_string(img) for img in images])
            elif file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
                return df.to_string(index=False)
            elif file_path.lower().endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
                return df.to_string(index=False)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        finally:
            if os.path.exists(file_path):
                os.unlink(file_path)
