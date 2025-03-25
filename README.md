# 🚀 Email Processing & Classification API

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction
This project automates email processing by extracting text and attachments (PDFs, images) and classifying the content using an AI-powered LLM. The goal is to streamline email-based workflows and improve response efficiency.

## 🎥 Demo
🔗 [Live Demo](#) (if applicable)  
📹 [Video Demo](#) (if applicable)  
🖼️ Screenshots:

![Screenshot 1](link-to-image)

## 💡 Inspiration
Managing large volumes of emails manually is inefficient. This project aims to automate email classification and response processing using AI, reducing human effort and error.

## ⚙️ What It Does
- Extracts text from email bodies, PDFs, and images
- Processes extracted data using an AI model
- Identifies request type, sub-request type, and extracted fields
- Detects duplicate requests

## 🛠️ How We Built It
- Used FastAPI for API development
- Utilized PyPDF2 and Tesseract OCR for text extraction
- Leveraged Google AI's Gemini model for classification
- Built structured JSON output for easy integration

## 🚧 Challenges We Faced
1. **Extracting text from attachments** - Used Tesseract for image OCR and PyPDF2 for PDFs.
2. **Handling email formats** - Emails vary in structure, so regex and NLP techniques were applied.
3. **Improving AI classification accuracy** - Fine-tuned prompts and used confidence scores.

## 🏃 How to Run
### Prerequisites
- Python 3.10 or higher
- Pip (Python package manager)
- Tesseract OCR (for image text extraction)

### Install Dependencies
```sh
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_google_ai_key
TESSERACT_PATH=/path/to/tesseract.exe (Windows) or /usr/bin/tesseract (Linux)
```

### Start the API Server
```sh
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### API Usage
#### **POST /process-emails**
Processes emails and classifies them.

**Request:**
```json
{
  "email_subject": "Account Issue - Unable to Login",
  "email_body": "I am unable to log into my account. Please help.",
  "attachments": ["base64_encoded_pdf", "base64_encoded_image"]
}
```

**Response:**
```json
{
  "request_type": {
    "type": "Adjustment",
    "confidence_score": 1
  },
  "sub_request_type": [],
  "extracted_fields": {
    "account_issue": "Unable to log into account, password reset request",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "is_duplicate": false,
  "duplicate_reason": null
}
```

#### **GET /health**
Checks if the API is running.
```json
{
  "status": "ok"
}
```

## 🏗️ Tech Stack
- 🔹 **Backend:** FastAPI, Python
- 🔹 **AI Model:** Google AI Gemini
- 🔹 **Data Processing:** Tesseract OCR, PyPDF2
- 🔹 **Email Integration:** Microsoft Graph API

## 👥 Team
- **Janardhan Reddy Chinthakunta** - [GitHub](#) | [LinkedIn](#)
- **Subhajit Ghosh** - [GitHub](#) | [LinkedIn](#)

---
**Version:** 1.0  
**License:** MIT

