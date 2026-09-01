"""
Security Utilities for Cryptographic Operations, Token Verification, and Hashing.
"""
import hmac
import hashlib
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.exceptions import AuthenticationException


def generate_jwt_token(payload: Dict[str, Any], expires_in_minutes: int = 60 * 24) -> str:
    """
    Generate JWT Token with expiration time.
    """
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT Token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationException("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationException("Invalid authentication token")
