"""
Unified API JSON Response Formatter.
"""
from typing import Any, Optional, Dict, Tuple
from flask import jsonify, Response
from datetime import datetime, timezone


def api_response(
    success: bool = True,
    data: Optional[Any] = None,
    message: str = "Success",
    error: Optional[Dict[str, Any]] = None,
    status_code: int = 200
) -> Tuple[Response, int]:
    """
    Generate standardized HTTP JSON response envelope.
    
    Format:
    {
        "success": true/false,
        "message": "Description message",
        "data": { ... },
        "error": { ... },
        "timestamp": "ISO-8601"
    }
    """
    payload = {
        "success": success,
        "message": message,
        "data": data,
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return jsonify(payload), status_code
