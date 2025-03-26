from typing import Dict, List, Optional
import re
import pandas as pd

FIELD_EXTRACTION_RULES = {
    "Money Movement - Inbound": {
        "priority_fields": ["amount", "account_number", "routing_number", "effective_date"],
        "sources": {
            "body": {
                "amount": [
                    # Specific pattern for loan payment shares
                    r"Your share of the USD [\d,]+\.\d{2}.*?payment is USD ([\d,]+\.\d{2})",
                    # General amount patterns
                    r"(?:we will remit|remittance).*?USD ([\d,]+\.\d{2})",
                    r"\bUSD\s*([\d,]+\.\d{2})\b(?!.*(?:total|global))",
                    r"(?:amount|payment).*?\$([\d,]+\.\d{2})"
                ],
                "account_number": [
                    r"(?i)account.*?(\d{4,20})",
                    r"(?i)acct.*?(\d{4,20})"
                ],
                "routing_number": [
                    r"(?i)ABA.*?(\d{8,9})",
                    r"(?i)routing.*?(\d{8,9})"
                ],
                "effective_date": [
                    r"(?i)effective.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                    r"(?i)date.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
                ]
            },
            "attachments": {
                "pdf": {
                    "amount": [
                        r"(?i)total.*?\$?([\d,]+\.\d{2})",
                        r"\bUSD\s*([\d,]+\.\d{2})\b"
                    ],
                    "date": [
                        r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
                        r"(?i)effective.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
                    ]
                },
                "excel": {
                    "amount_columns": ["Amount", "Value", "Payment"],
                    "date_columns": ["Date", "Effective Date"]
                }
            }
        }
    },
    "Money Movement - Outbound": {
        "priority_fields": ["amount", "account_number", "routing_number", "effective_date", "currency"],
        "sources": {
            "body": {
                "amount": [
                    r"(?i)amount[\s:]*\$?([\d,]+\.\d{2})",
                    r"(?i)transfer.*\$?([\d,]+\.\d{2})"
                ],
                "account_number": [
                    r"(?i)account.*?(\d{4,20})",
                    r"(?i)acct.*?(\d{4,20})"
                ],
                "routing_number": [
                    r"(?i)ABA.*?(\d{8,9})",
                    r"(?i)routing.*?(\d{8,9})"
                ],
                "effective_date": [
                    r"(?i)effective.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                    r"(?i)date.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
                ],
                "currency": [
                    r"(?i)currency.*?([A-Z]{3})",
                    r"(?i)payment.*?in\s+([A-Z]{3})"
                ]
            },
            "attachments": {
                "pdf": {
                    "amount": [
                        r"(?i)total.*?\$?([\d,]+\.\d{2})",
                        r"\b([A-Z]{3})\s*([\d,]+\.\d{2})\b"
                    ],
                    "currency": [
                        r"(?i)currency.*?([A-Z]{3})"
                    ]
                }
            }
        }
    },
    "Adjustment": {
        "priority_fields": ["adjustment_amount", "effective_date", "deal_name", "previous_balance", "new_balance"],
        "sources": {
            "body": {
                "adjustment_amount": [
                    r"(?i)adjustment.*?\$?([\d,]+\.\d{2})",
                    r"(?i)change.*?\$?([\d,]+\.\d{2})"
                ],
                "effective_date": [
                    r"(?i)effective.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
                ],
                "deal_name": [
                    r"(?i)deal.*?name.*?([A-Z0-9].*?\b)",
                    r"(?i)reference.*?([A-Z0-9].*?\b)"
                ],
                "previous_balance": [
                    r"(?i)previous.*?balance.*?\$?([\d,]+\.\d{2})"
                ],
                "new_balance": [
                    r"(?i)new.*?balance.*?\$?([\d,]+\.\d{2})"
                ]
            }
        }
    },
    "AU Transfer": {
        "priority_fields": ["transfer_type", "amount", "deal_name", "effective_date"],
        "sources": {
            "body": {
                "transfer_type": [
                    r"(?i)reallocation\s*(fees|principal)",
                    r"(?i)amendment\s*fees"
                ],
                "amount": [
                    r"(?i)amount.*?\$?([\d,]+\.\d{2})"
                ],
                "deal_name": [
                    r"(?i)deal.*?name.*?([A-Z0-9].*?\b)"
                ]
            }
        }
    },
    "Closing Notice": {
        "priority_fields": ["notice_type", "effective_date", "deal_name", "change_amount"],
        "sources": {
            "body": {
                "notice_type": [
                    r"(?i)cashless\s*roll",
                    r"(?i)(decrease|increase)\s*in\s*commitment"
                ],
                "change_amount": [
                    r"(?i)change.*?\$?([\d,]+\.\d{2})"
                ],
                "deal_name": [
                    r"(?i)deal.*?name.*?([A-Z0-9].*?\b)"
                ]
            }
        }
    },
    "Commitment Change": {
        "priority_fields": ["new_commitment", "previous_commitment", "effective_date", "deal_name"],
        "sources": {
            "body": {
                "new_commitment": [
                    r"(?i)new.*?commitment.*?\$?([\d,]+\.\d{2})"
                ],
                "previous_commitment": [
                    r"(?i)previous.*?commitment.*?\$?([\d,]+\.\d{2})"
                ],
                "deal_name": [
                    r"(?i)deal.*?name.*?([A-Z0-9].*?\b)"
                ]
            }
        }
    },
    "Fee Payment": {
        "priority_fields": ["fee_type", "amount", "due_date", "deal_name"],
        "sources": {
            "body": {
                "fee_type": [
                    r"(?i)ongoing\s*fee",
                    r"(?i)letter\s*of\s*credit\s*fee"
                ],
                "amount": [
                    r"(?i)amount.*?\$?([\d,]+\.\d{2})",
                    r"(?i)fee.*?\$?([\d,]+\.\d{2})"
                ],
                "due_date": [
                    r"(?i)due.*?date.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
                ],
                "deal_name": [
                    r"(?i)deal.*?name.*?([A-Z0-9].*?\b)"
                ]
            }
        }
    }
}


class FieldExtractor:
    def __init__(self, request_type: str):
        self.rules = FIELD_EXTRACTION_RULES.get(request_type, {})
        self.request_type = request_type

    def extract_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract fields from email body text"""
        results = {}
        if not text or not self.rules.get("sources", {}).get("body"):
            return results

        for field, patterns in self.rules["sources"]["body"].items():
            if isinstance(patterns, list):
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        # Handle multiple capture groups
                        if matches and isinstance(matches[0], tuple):
                            # For patterns with multiple groups, flatten the results
                            flat_matches = [item for match in matches for item in match if item]
                            if flat_matches:
                                results.setdefault(field, []).extend(flat_matches)
                        else:
                            results.setdefault(field, []).extend(matches)
        return results

    def extract_from_attachment(self, file_path: str, text_content: str) -> Dict[str, List[str]]:
        """Extract fields from attachment content"""
        results = {}
        if not text_content or not self.rules.get("sources", {}).get("attachments"):
            return results

        file_ext = file_path.split('.')[-1].lower()

        if file_ext == 'pdf':
            for field, patterns in self.rules["sources"]["attachments"].get("pdf", {}).items():
                for pattern in patterns:
                    matches = re.findall(pattern, text_content)
                    if matches:
                        if matches and isinstance(matches[0], tuple):
                            flat_matches = [item for match in matches for item in match if item]
                            if flat_matches:
                                results.setdefault(field, []).extend(flat_matches)
                        else:
                            results.setdefault(field, []).extend(matches)

        elif file_ext in ['xls', 'xlsx']:
            try:
                df = pd.read_excel(file_path)
                excel_rules = self.rules["sources"]["attachments"].get("excel", {})

                # Extract amounts from specified columns
                for amount_col in excel_rules.get("amount_columns", []):
                    if amount_col in df.columns:
                        amounts = df[amount_col].dropna()
                        if not amounts.empty:
                            # Convert to string and clean
                            amounts = amounts.astype(str).str.extract(r'(\d+\.\d{2})')[0].dropna().tolist()
                            if amounts:
                                results.setdefault("amount", []).extend(amounts)

                # Extract dates from specified columns
                for date_col in excel_rules.get("date_columns", []):
                    if date_col in df.columns:
                        dates = df[date_col].dropna().astype(str).tolist()
                        if dates:
                            results.setdefault("effective_date", []).extend(dates)

                # Special handling for deal name if present
                if "deal_name" in self.rules["priority_fields"]:
                    for col in df.columns:
                        if "deal" in str(col).lower() or "name" in str(col).lower():
                            names = df[col].dropna().astype(str).tolist()
                            if names:
                                results.setdefault("deal_name", []).extend(names)

            except Exception as e:
                print(f"Error processing Excel file: {str(e)}")

        return results

    def get_priority_fields(self) -> List[str]:
        """Get the priority fields for this request type"""
        return self.rules.get("priority_fields", [])