import google.generativeai as genai
import json
import hashlib
import re
from ..models.extracted_data import ExtractedData
from ..models.request_type_mapping import REQUEST_TYPES, REQUEST_PRIORITY

class Classifier:
    def __init__(self, api_key: str):
        genai.configure(api_key='')
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    def classify(self, content: str) -> ExtractedData:
        print(content)
        prompt = f"""
        Analyze this banking service request and classify it according to these types:
        {json.dumps(REQUEST_TYPES, indent=2)}
        
        Content: {content}
        
        Return JSON format with:
        - request_type (with confidence_score)
        - sub_request_type (if applicable)
        - extracted_fields (amount, date, account details, etc.)
        - is_duplicate (boolean)
        - duplicate_reason (if applicable)
        """
        
        try:
            response = self.model.generate_content(prompt)
            raw_text = response.text.strip()
            print(response)
            # 🔍 Remove any unwanted "```json" or "```"
            cleaned_text = re.sub(r"^```json|```$", "", raw_text).strip()
            result = json.loads(cleaned_text)
            extracted_data = ExtractedData.from_llm_response(result, REQUEST_PRIORITY)
            return extracted_data
        except Exception as e:
            raise Exception(f"Classification failed: {str(e)}")


    def compute_hash(self, email_content: str) -> str:
        """Generate a hash for duplicate detection."""
        return hashlib.sha256(email_content.encode()).hexdigest()