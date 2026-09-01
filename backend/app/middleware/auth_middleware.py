"""
Authentication & Authorization Middleware Decorators.
"""
from functools import wraps
from flask import request, g
from app.core.exceptions import AuthenticationException, AuthorizationException
from app.core.security import decode_jwt_token


def require_auth(f):
    """
    Decorator enforcing valid Bearer JWT token in Authorization header.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            raise AuthenticationException("Missing Authorization Header")
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationException("Authorization Header must be in format 'Bearer <token>'")
        
        token = parts[1]
        payload = decode_jwt_token(token)
        g.user = payload
        return f(*args, **kwargs)
    return decorated_function


def require_role(roles: list):
    """
    Decorator enforcing specific user roles.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, "user") or not g.user:
                raise AuthenticationException("User identity not established")
            user_role = g.user.get("role", "patient")
            if user_role not in roles:
                raise AuthorizationException(f"Role '{user_role}' is not authorized to perform this operation")
            return f(*args, **kwargs)
        return decorated_function
    return decorator
