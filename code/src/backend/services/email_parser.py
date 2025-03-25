import email
from email import policy
import tempfile
from typing import Dict, List
import os

class EmailParser:
    @staticmethod
    def parse_eml(file_path: str) -> Dict:
        with open(file_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
        
        result = {
            'headers': {
                'subject': msg['subject'],
                'from': msg['from'],
                'to': msg['to'],
                'date': msg['date'],
                'cc': msg['cc'] or ""
            },
            'body': "",
            'attachments': []
        }
        
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                result['body'] += part.get_content()
            elif part.get_filename():
                with tempfile.NamedTemporaryFile(delete=False, suffix=part.get_filename()) as tmp:
                    tmp.write(part.get_payload(decode=True))
                    result['attachments'].append({
                        'filename': part.get_filename(),
                        'path': tmp.name,
                        'content_type': part.get_content_type()
                    })
        return result