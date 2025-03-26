from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any, List
from enum import Enum


class PriorityLevel(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    UNKNOWN = 99


class ExtractedData(BaseModel):
    request_type: str
    sub_request_type: Optional[str] = None
    confidence_score: float
    extracted_fields: Dict[str, Any]
    is_duplicate: bool = False
    priority: PriorityLevel = PriorityLevel.UNKNOWN
    duplicate_reason: Optional[str] = None
    raw_content: Optional[Dict[str, Any]] = None

    @field_validator('sub_request_type', mode='before')
    def handle_empty_sub_request(cls, v):
        if isinstance(v, list):
            return None if not v else v[0]
        return v

    @classmethod
    def from_llm_response(cls, response_data: dict, priority_mapping: dict):
        """Convert LLM response into a properly formatted ExtractedData object."""
        request_type = response_data.get("type", "Unknown")
        priority_value = priority_mapping.get(request_type, 99)

        # Handle sub_request_type conversion
        sub_type = response_data.get("sub_type")

        try:
            priority = PriorityLevel(priority_value)
        except ValueError:
            priority = PriorityLevel.UNKNOWN

        return cls(
            request_type=request_type,
            sub_request_type=sub_type,
            confidence_score=response_data.get("confidence_score", 0.0),
            extracted_fields={
                k: ", ".join(v) if isinstance(v, list) else (str(v) if v is not None else "N/A")
                for k, v in response_data.get("extracted_fields", {}).items()
            },
            priority=priority,
            is_duplicate=response_data.get("is_duplicate", False),
            duplicate_reason=response_data.get("duplicate_reason"),
        )