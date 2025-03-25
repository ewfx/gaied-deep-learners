from pydantic import BaseModel
from typing import Optional, List, Dict

class ExtractedData(BaseModel):
    request_type: str
    sub_request_type: Optional[str]
    confidence_score: float
    extracted_fields: Dict[str, str]
    is_duplicate: bool
    duplicate_reason: Optional[str]
    raw_content: Optional[str] = None