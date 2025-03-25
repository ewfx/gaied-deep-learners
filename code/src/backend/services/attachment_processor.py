import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import os
from typing import Optional

class AttachmentProcessor:
    def __init__(self, tesseract_path: Optional[str] = None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def extract_text(self, file_path: str) -> str:
        try:
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                return pytesseract.image_to_string(file_path)
            elif file_path.lower().endswith('.pdf'):
                try:
                    with open(file_path, 'rb') as f:
                        reader = PdfReader(f)
                        text = "\n".join([page.extract_text() or "" for page in reader.pages])
                        if text.strip():
                            return text
                    images = convert_from_path(file_path)
                    return "\n".join([pytesseract.image_to_string(img) for img in images])
                except Exception as e:
                    raise Exception(f"PDF processing failed: {str(e)}")
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        finally:
            if os.path.exists(file_path):
                os.unlink(file_path)