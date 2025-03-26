from typing import Dict, List, Optional
from ..models.extracted_data import ExtractedData, PriorityLevel

ROUTING_RULES = {
    "Money Movement - Inbound": {
        "team": "Payments Processing",
        "required_skills": ["payment_verification", "fraud_detection"],
        "priority_threshold": 0.8,
        "priority_mapping": {
            PriorityLevel.CRITICAL: "Senior Processor",
            PriorityLevel.HIGH: "Processor II",
            PriorityLevel.MEDIUM: "Processor I",
            PriorityLevel.LOW: "Junior Processor"
        }
    },
    "Money Movement - Outbound": {
        "team": "Payments Processing",
        "required_skills": ["payment_verification", "compliance_check"],
        "priority_threshold": 0.8,
        "priority_mapping": {
            PriorityLevel.CRITICAL: "Senior Processor",
            PriorityLevel.HIGH: "Processor II",
            PriorityLevel.MEDIUM: "Processor I",
            PriorityLevel.LOW: "Junior Processor"
        }
    },
    "Adjustment": {
        "team": "Account Management",
        "required_skills": ["account_reconciliation"],
        "priority_threshold": 0.7,
        "priority_mapping": {
            PriorityLevel.CRITICAL: "Account Manager",
            PriorityLevel.HIGH: "Senior Account Specialist",
            PriorityLevel.MEDIUM: "Account Specialist",
            PriorityLevel.LOW: "Junior Account Specialist"
        }
    },
    # Add other request types...
}


class RequestRouter:
    def __init__(self, available_teams: Dict[str, List[str]]):
        """
        available_teams: Dict of team names to list of skills
        """
        self.teams = available_teams

    def route_request(self, request: ExtractedData) -> Dict:
        """Determine the appropriate route for a request"""
        routing_info = ROUTING_RULES.get(request.request_type, {})

        if not routing_info:
            return {
                "team": "Unassigned",
                "assignee": None,
                "reason": "No routing rule for this request type",
                "auto_assign": False
            }

        # Check if any team has the required skills
        suitable_teams = [
            team for team, skills in self.teams.items()
            if all(skill in skills for skill in routing_info.get("required_skills", []))
               and team == routing_info.get("team")
        ]

        if not suitable_teams:
            return {
                "team": "Unassigned",
                "assignee": None,
                "reason": "No team with required skills available",
                "auto_assign": False
            }

        # Determine specific assignee based on priority
        assignee = None
        if request.confidence_score >= routing_info.get("priority_threshold", 0.7):
            priority_mapping = routing_info.get("priority_mapping", {})
            assignee = priority_mapping.get(request.priority, "Unassigned")

        return {
            "team": suitable_teams[0],
            "assignee": assignee,
            "request_type": request.request_type,
            "priority": request.priority.name,
            "confidence_score": request.confidence_score,
            "auto_assign": request.confidence_score >= routing_info.get("priority_threshold", 0.7)
        }