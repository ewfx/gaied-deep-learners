import google.generativeai as genai
import json
import hashlib
import re
from typing import List, Dict
from ..models.extracted_data import ExtractedData
from ..models.multi_request_data import MultiRequestData
from ..models.request_type_mapping import REQUEST_TYPES, REQUEST_PRIORITY


class Classifier:
    def __init__(self, api_key: str):
        genai.configure(api_key='')
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def classify(self, content: str) -> MultiRequestData:
        prompt = f"""
        Analyze this banking service request email and perform the following tasks:

        1. Identify ALL request types present in the email from these options:
        {json.dumps(REQUEST_TYPES, indent=2)}

        2. For each request found:
           - Determine the request type and sub-type (if applicable)
           - Sub-type (must be one of the listed sub-types or null/empty)
           - Extract relevant fields (amount, date, account details, etc.)
           - Provide a confidence score (0-1)

        3. Determine the PRIMARY request (main intent of the sender)

        4. Check for duplicate requests by comparing with previous emails

        Return JSON format with:
        - primary_request (with type, sub_type [string or null], confidence_score, extracted_fields)
        - secondary_requests (array of other requests found)
        - is_duplicate (boolean)
        - duplicate_reason (if applicable)

        Email Content: {content}
        """

        try:
            response = self.model.generate_content(prompt)
            print(response)
            raw_text = response.text.strip()
            cleaned_text = re.sub(r"^```json|```$", "", raw_text).strip()
            result = json.loads(cleaned_text)

            # Ensure sub_request_type is properly formatted
            if "primary_request" in result:
                result["primary_request"]["sub_type"] = self._clean_sub_type(result["primary_request"].get("sub_type"))

            if "secondary_requests" in result:
                for req in result["secondary_requests"]:
                    req["sub_type"] = self._clean_sub_type(req.get("sub_type"))

            return MultiRequestData.from_llm_response(result, REQUEST_PRIORITY)
        except Exception as e:
            raise Exception(f"Classification failed: {str(e)}")

    def _clean_sub_type(self, sub_type):
        """Ensure sub_type is either a valid string or None"""
        if isinstance(sub_type, list):
            return sub_type[0] if sub_type else None
        return sub_type if sub_type else None

    def compute_hash(self, subject: str, sender: str, sent_date: str, email_body: str) -> str:
        """Generate a hash for deduplication using only key fields."""
        key_content = self.extract_key_content(email_body)  # Extract meaningful content
        unique_string = f"{subject.lower()}|{sender.lower()}|{sent_date}|{key_content.lower()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()

    def extract_key_content(self, email_body: str) -> str:
        """
        Extract meaningful content from the email body for deduplication.
        Removes signatures, greetings, timestamps, and unnecessary lines.
        """
        lines = email_body.split("\n")
        filtered_lines = []

        for line in lines:
            if not line.strip():  # Skip empty lines
                continue
            if line.lower().startswith(("regards", "best regards", "sincerely", "thanks", "generated on")):
                break  # Stop processing at common signature indicators
            filtered_lines.append(line.strip())

        return " ".join(filtered_lines[:500])  # Take only the first 500 characters

    def detect_duplicates(self, subject: str, sender: str, sent_date: str, email_body: str, previous_hashes: List[str]) -> dict:
        """Improved duplicate detection using refined email hashing."""
        current_hash = self.compute_hash(subject, sender, sent_date, email_body)

        # Basic duplicate check
        if current_hash in previous_hashes:
            return {
                "is_duplicate": True,
                "reason": "Exact content match (excluding signatures/timestamps)",
                "hash": current_hash
            }

        # Thread analysis (kept same)
        thread_info = self._analyze_thread(email_body)
        if thread_info.get("is_thread"):
            return {
                "is_duplicate": True,
                "reason": f"Part of thread: {thread_info['thread_type']}",
                "hash": current_hash,
                "thread_data": thread_info
            }

        return {
            "is_duplicate": False,
            "hash": current_hash
        }

    def _analyze_thread(self, content: str) -> dict:
        """Analyze email for thread characteristics"""
        patterns = {
            "forward": r"(?i)^\s*-----Original Message-----",
            "reply": r"(?i)^\s*On.*wrote:",
            "quoted": r"(?i)^>"
        }

        for thread_type, pattern in patterns.items():
            if re.search(pattern, content, re.MULTILINE):
                return {
                    "is_thread": True,
                    "thread_type": thread_type,
                    "original_content": self._extract_original_content(content, thread_type)
                }

        return {"is_thread": False}

    def _extract_original_content(self, content: str, thread_type: str) -> str:
        """Extract original message from thread"""
        if thread_type == "forward":
            return re.split(r"(?i)-----Original Message-----", content)[-1]
        elif thread_type == "reply":
            return re.split(r"(?i)On.*wrote:", content)[-1]
        return content
