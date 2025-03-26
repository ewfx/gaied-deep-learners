import email
from email import policy
import tempfile
from typing import Dict, List
import extract_msg  # New import for MSG support
from pathlib import Path
from ..preprocessing.text_cleaning import EmailCleaner


class EmailParser:
    @staticmethod
    def parse_eml(file_path: str) -> Dict:
        """Parse EML format emails"""
        with open(file_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
        return EmailParser._parse_email_message(msg)

    @staticmethod
    def parse_msg(file_path: str) -> Dict:
        """Parse Outlook MSG format emails"""
        msg = extract_msg.Message(file_path)
        result = {
            'headers': {
                'subject': msg.subject or "",
                'from': msg.sender or "",
                'to': msg.to or "",
                'date': str(msg.date) if msg.date else "",
                'cc': msg.cc or ""
            },
            'body': msg.body or "",
            'attachments': []
        }

        # Process MSG attachments
        for attachment in msg.attachments:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(attachment.longFilename).suffix) as tmp:
                if hasattr(attachment, 'data'):
                    tmp.write(attachment.data)
                else:
                    tmp.write(attachment._getStream('__substg1.0_37010102'))
                result['attachments'].append({
                    'filename': attachment.longFilename,
                    'path': tmp.name,
                    'content_type': attachment.type or "application/octet-stream"
                })

        msg.close()
        return result

    @staticmethod
    def _parse_email_message(msg) -> Dict:
        """Shared parser for email.message objects"""
        result = {
            'headers': {
                'subject': msg['subject'] or "",
                'from': msg['from'] or "",
                'to': msg['to'] or "",
                'date': msg['date'] or "",
                'cc': msg['cc'] or ""
            },
            'body': "",
            'attachments': []
        }

        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                charset = part.get_content_charset() or 'utf-8'
                try:
                    body_content = part.get_content()
                    if isinstance(body_content, bytes):
                        body_content = body_content.decode(charset)
                    result['body'] += body_content
                except Exception:
                    continue
            elif part.get_filename():
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(part.get_filename()).suffix) as tmp:
                    tmp.write(part.get_payload(decode=True))
                    result['attachments'].append({
                        'filename': part.get_filename(),
                        'path': tmp.name,
                        'content_type': part.get_content_type()
                    })

        return result

    @staticmethod
    def parse_email(file_path: str) -> Dict:
        """Main entry point that detects and routes to appropriate parser"""
        if file_path.lower().endswith('.msg'):
            result =  EmailParser.parse_msg(file_path)
        else:  # Default to EML parser
            result = EmailParser.parse_eml(file_path)

        # Clean email content before returning it
        cleaner = EmailCleaner()
        result['body'] = cleaner.clean_email_content(result['body'])
        return result