import tempfile

import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import pandas as pd
import os
import extract_msg
from pathlib import Path
from typing import Optional, Dict, List
import email
from email import policy


class AttachmentProcessor:
    def __init__(self, tesseract_path: str):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def extract_text(self, file_path: str) -> Optional[str]:
        """Extracts text from various file types including MSG files."""
        try:
            if not os.path.exists(file_path):
                return None

            file_ext = Path(file_path).suffix.lower()

            if file_ext in ('.png', '.jpg', '.jpeg'):
                return pytesseract.image_to_string(file_path)
            elif file_ext == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_ext == '.msg':
                return self._extract_from_msg(file_path)
            elif file_ext == '.csv':
                return self._extract_from_csv(file_path)
            elif file_ext in ('.xls', '.xlsx'):
                return self._extract_from_excel(file_path)
            elif file_ext in ('.eml', '.txt'):
                return self._extract_from_text_file(file_path)
            else:
                # Fallback for unknown file types
                return self._try_generic_extraction(file_path)

        except Exception as e:
            print(f"Error processing attachment: {str(e)}")
            return None
        finally:
            if os.path.exists(file_path):
                os.unlink(file_path)

    def _extract_from_pdf(self, file_path: str) -> Optional[str]:
        """Extract text from PDF files with OCR fallback"""
        # First try direct text extraction
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            if text.strip():
                return text

        # Fallback to OCR if no text found
        images = convert_from_path(file_path)
        return "\n".join([pytesseract.image_to_string(img) for img in images])

    def _extract_from_msg(self, file_path: str) -> Optional[str]:
        """Extract text content from Outlook MSG files"""
        try:
            msg = extract_msg.Message(file_path)
            content = f"""
            Subject: {msg.subject or 'N/A'}
            From: {msg.sender or 'N/A'}
            To: {msg.to or 'N/A'}
            CC: {msg.cc or 'N/A'}
            Date: {msg.date or 'N/A'}

            Body:
            {msg.body or 'No body content'}
            """

            # Process attachments recursively
            if msg.attachments:
                content += "\n\n--- ATTACHMENTS ---\n"
                for attachment in msg.attachments:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(attachment.longFilename).suffix) as tmp:
                        if hasattr(attachment, 'data'):
                            tmp.write(attachment.data)
                        else:
                            tmp.write(attachment._getStream('__substg1.0_37010102'))
                        tmp_path = tmp.name

                    # Recursively process attachment content
                    attachment_content = self.extract_text(tmp_path)
                    if attachment_content:
                        content += f"\nAttachment: {attachment.longFilename}\n{attachment_content}\n"

                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

            msg.close()
            return content
        except Exception as e:
            print(f"Error processing MSG file: {str(e)}")
            return None

    def _extract_from_csv(self, file_path: str) -> Optional[str]:
        """Extract text from CSV files"""
        try:
            df = pd.read_csv(file_path)
            return df.to_string(index=False)
        except Exception:
            # Fallback to raw text if CSV parsing fails
            return self._extract_from_text_file(file_path)

    def _extract_from_excel(self, file_path: str) -> Optional[str]:
        """Extract text from Excel files"""
        try:
            df = pd.read_excel(file_path)
            return df.to_string(index=False)
        except Exception:
            # Fallback to raw text if Excel parsing fails
            return self._extract_from_text_file(file_path)

    def _extract_from_text_file(self, file_path: str) -> Optional[str]:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try binary read as last resort
            with open(file_path, 'rb') as f:
                return str(f.read())

    def _try_generic_extraction(self, file_path: str) -> Optional[str]:
        """Fallback method for unknown file types"""
        try:
            # First try as text file
            result = self._extract_from_text_file(file_path)
            if result and len(result) > 10:  # Simple validity check
                return result

            # Then try as binary
            with open(file_path, 'rb') as f:
                binary_content = f.read()
                if b'\x00' not in binary_content:  # Basic binary check
                    return binary_content.decode('utf-8', errors='ignore')

            return f"Binary file: {Path(file_path).name}"
        except Exception:
            return None

    def process_attachments(self, attachments: List[Dict]) -> List[Dict]:
        """Process a list of attachments and return enriched data"""
        processed = []
        for attachment in attachments:
            try:
                content = self.extract_text(attachment['path'])
                processed.append({
                    'filename': attachment['filename'],
                    'content_type': attachment['content_type'],
                    'content': content,
                    'size': os.path.getsize(attachment['path']) if os.path.exists(attachment['path']) else 0
                })
            except Exception as e:
                print(f"Error processing attachment {attachment['filename']}: {str(e)}")
                processed.append({
                    'filename': attachment['filename'],
                    'content_type': attachment['content_type'],
                    'error': str(e)
                })
        return processed