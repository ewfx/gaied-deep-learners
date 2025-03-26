from pydantic import BaseModel
from typing import Optional, Dict, Any

class ExtractedData(BaseModel):
    request_type: str
    sub_request_type: Optional[str] = None
    confidence_score: float
    extracted_fields: Dict[str, Any]
    is_duplicate: bool
    priority: int
    duplicate_reason: Optional[str] = None
    raw_content: Optional[str] = None

    @classmethod
    def from_llm_response(cls, response_data: dict, priority_mapping: dict):
        """Convert LLM response into a properly formatted ExtractedData object."""
        request_type = response_data.get("request_type", {}).get("type", "Unknown")
        return cls(
            request_type=request_type,
            confidence_score=response_data.get("request_type", {}).get("confidence_score", 0.0),
            sub_request_type = response_data.get("sub_request_type", ""),
            extracted_fields={
                k: ", ".join(v) if isinstance(v, list) else (str(v) if v is not None else "N/A")
                for k, v in response_data.get("extracted_fields", {}).items()
            },
            priority=priority_mapping.get(request_type, 99),  # Assign priority or default (99 if unknown)
            is_duplicate=response_data.get("is_duplicate", False),
            duplicate_reason=response_data.get("duplicate_reason"),
            raw_content=response_data.get("raw_content"),
        )
