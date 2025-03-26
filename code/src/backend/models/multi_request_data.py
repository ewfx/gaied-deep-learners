from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from backend.models.extracted_data import ExtractedData


class MultiRequestData(BaseModel):
    primary_request: ExtractedData
    secondary_requests: List[ExtractedData] = []
    is_thread: bool = False
    thread_relations: Dict[str, str] = {}
    raw_content: Optional[Dict[str, Any]] = None

    @classmethod
    def from_llm_response(cls, response_data: dict, priority_mapping: dict):
        primary = ExtractedData.from_llm_response(
            response_data["primary_request"],
            priority_mapping
        )

        secondaries = [
            ExtractedData.from_llm_response(req, priority_mapping)
            for req in response_data.get("secondary_requests", [])
        ]

        return cls(
            primary_request=primary,
            secondary_requests=secondaries,
            is_thread=response_data.get("is_thread", False),
            thread_relations=response_data.get("thread_relations", {}),
            raw_content=response_data.get("raw_content")
        )