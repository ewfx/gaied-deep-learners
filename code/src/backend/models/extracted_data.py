from typing import Optional, Dict

from pydantic import BaseModel

from pydantic import BaseModel
from typing import Optional, Dict, Any

class ExtractedData(BaseModel):
    request_type: str
    sub_request_type: Optional[str] = None
    confidence_score: float
    extracted_fields: Dict[str, Any]
    is_duplicate: bool
    duplicate_reason: Optional[str] = None
    raw_content: Optional[str] = None

    @classmethod
    def from_llm_response(cls, response_data: dict):
        """Convert LLM response into a properly formatted ExtractedData object."""
        return cls(
            request_type=response_data.get("request_type", {}).get("value", "Unknown"),
            confidence_score=response_data.get("request_type", {}).get("confidence_score", 0.0),
            sub_request_type=", ".join(response_data.get("sub_request_type", [])) if response_data.get("sub_request_type") else None,
            extracted_fields={
                k: ", ".join(v) if isinstance(v, list) else (str(v) if v is not None else "N/A")
                for k, v in response_data.get("extracted_fields", {}).items()
            },
            is_duplicate=response_data.get("is_duplicate", False),
            duplicate_reason=response_data.get("duplicate_reason"),
            raw_content=response_data.get("raw_content"),
        )
