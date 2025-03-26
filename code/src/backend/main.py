from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.services.email_parser import EmailParser
from backend.services.attachment_processor import AttachmentProcessor
from backend.services.classification import Classifier
from backend.services.routing import RequestRouter
from backend.config import Config
from backend.models.multi_request_data import MultiRequestData
import tempfile
import os
from typing import Dict, List

app = FastAPI()
config = Config()
config.validate()

# Sample available teams and skills (replace with your actual data)
available_teams = {
    "Payments Processing": ["payment_verification", "fraud_detection", "compliance_check"],
    "Account Management": ["account_reconciliation", "customer_service"],
    "Loan Services": ["loan_processing", "document_verification"]
}
router = RequestRouter(available_teams)

# In-memory store for demo (replace with DB in production)
processed_hashes = set()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/process")
async def process_email(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Process email using the universal parser
        email_data = EmailParser.parse_email(tmp_path)  # Changed to use parse_email
        processor = AttachmentProcessor(config.tesseract_path)

        # Process attachments and extract text
        attachments_data = []
        for attachment in email_data['attachments']:
            text = processor.extract_text(attachment['path'])
            attachments_data.append({
                'filename': attachment['filename'],
                'content_type': attachment['content_type'],
                'text': text
            })

        # Build full content with structured attachment data
        content_str = f"""
        EMAIL HEADERS:
        From: {email_data['headers']['from']}
        To: {email_data['headers']['to']}
        CC: {email_data['headers']['cc']}
        Subject: {email_data['headers']['subject']}
        Date: {email_data['headers']['date']}

        BODY:
        {email_data['body']}

        ATTACHMENTS:
        {'\n\n'.join(f"{a['filename']}:\n{a['text']}" for a in attachments_data)}
        """
        print(f"Parsed headers: {email_data['headers']}")  # Debug print
        # Classify content
        classifier = Classifier(config.gemini_api_key)
        print(email_data['headers']['subject'])

        # Detect duplicates with the new signature
        duplicate_info = classifier.detect_duplicates(
            subject=email_data['headers']['subject'],
            sender=email_data['headers']['from'],
            sent_date=email_data['headers']['date'],
            email_body=email_data['body'],
            previous_hashes=list(processed_hashes)
        )
        processed_hashes.add(duplicate_info['hash'])

        if duplicate_info['is_duplicate']:
            return {
                "status": "duplicate",
                "reason": duplicate_info['reason'],
                "hash": duplicate_info['hash']
            }

        # Perform classification
        result = classifier.classify(content_str)
        result.raw_content = {
            'headers': email_data['headers'],
            'body': email_data['body'],
            'attachments': attachments_data
        }

        # Enhanced field extraction
        _enhance_with_field_extraction(result, email_data['body'], attachments_data)

        # Route requests
        routing_decisions = {
            "primary": router.route_request(result.primary_request),
            "secondary": [router.route_request(req) for req in result.secondary_requests]
        }

        return {
            "classification": result.dict(),
            "routing": routing_decisions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _enhance_with_field_extraction(result: MultiRequestData, body: str, attachments: List[Dict]):
    """Enhance results with rule-based field extraction"""
    from backend.services.field_extraction_rules import FieldExtractor

    # Process primary request
    primary_extractor = FieldExtractor(result.primary_request.request_type)
    body_fields = primary_extractor.extract_from_text(body)

    # Process attachments for primary request
    attachment_fields = {}
    for attachment in attachments:
        if attachment['text']:
            fields = primary_extractor.extract_from_attachment(
                attachment['filename'],
                attachment['text']
            )
            for k, v in fields.items():
                attachment_fields.setdefault(k, []).extend(v)

    # Update extracted fields
    result.primary_request.extracted_fields.update({
        **body_fields,
        **attachment_fields
    })

    # Process secondary requests
    for req in result.secondary_requests:
        extractor = FieldExtractor(req.request_type)
        req.extracted_fields.update(extractor.extract_from_text(body))
        for attachment in attachments:
            if attachment['text']:
                req.extracted_fields.update(
                    extractor.extract_from_attachment(attachment['filename'], attachment['text'])
                )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)