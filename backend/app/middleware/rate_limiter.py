"""
Simple In-Memory Rate Limiter Middleware for API Protection.
"""
import time
from functools import wraps
from flask import request
from app.core.exceptions import BaseAppException

# IP request timestamps cache
_ip_requests = {}


def rate_limit(limit: int = 100, window_seconds: int = 60):
    """
    In-memory rate limiter decorator.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr or "127.0.0.1"
            now = time.time()

            if ip not in _ip_requests:
                _ip_requests[ip] = []

            # Clean expired timestamps
            _ip_requests[ip] = [ts for ts in _ip_requests[ip] if now - ts < window_seconds]

            if len(_ip_requests[ip]) >= limit:
                raise BaseAppException(
                    message=f"Rate limit exceeded. Maximum {limit} requests per {window_seconds} seconds.",
                    status_code=429,
                    error_code="RATE_LIMIT_EXCEEDED"
                )

            _ip_requests[ip].append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
