"""
Input Validation Helper Functions.
"""
import re
from typing import Dict, Any, List
from app.core.exceptions import ValidationException


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    """
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(regex, email):
        raise ValidationException("Invalid email address format")
    return True


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Ensure all required fields are present in data dictionary.
    """
    if not data:
        raise ValidationException("Request payload cannot be empty")
    missing = [field for field in required_fields if field not in data or data[field] is None or data[field] == ""]
    if missing:
        raise ValidationException(f"Missing required fields: {', '.join(missing)}")
