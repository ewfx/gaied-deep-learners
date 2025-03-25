from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.services.email_parser import EmailParser
from backend.services.attachment_processor import AttachmentProcessor
from backend.services.classification import Classifier
from backend.config import Config
import tempfile
import os

app = FastAPI()
config = Config()
config.validate()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process")
async def process_email(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        
        # Process email
        email_data = EmailParser().parse_eml(tmp_path)
        processor = AttachmentProcessor(config.tesseract_path)
        attachments_text = []
        
        for attachment in email_data['attachments']:
            text = processor.extract_text(attachment['path'])
            attachments_text.append(f"{attachment['filename']}:\n{text}")
        
        full_content = f"""
        EMAIL HEADERS:
        From: {email_data['headers']['from']}
        To: {email_data['headers']['to']}
        CC: {email_data['headers']['cc']}
        Subject: {email_data['headers']['subject']}
        Date: {email_data['headers']['date']}
        
        BODY:
        {email_data['body']}
        
        ATTACHMENTS:
        {'\n\n'.join(attachments_text)}
        """
        
        # Classify content
        classifier = Classifier(config.gemini_api_key)
        result = classifier.classify(full_content)
        result.raw_content = full_content
        
        return result.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)