"""
Application Exception Hierarchy for Structured Error Responses.
"""
from typing import Optional, Dict, Any


class BaseAppException(Exception):
    """
    Base Exception class for custom application errors.
    """
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        payload: Optional[Dict[str, Any]] = None,
        error_code: str = "BAD_REQUEST"
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}
        self.error_code = error_code

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize exception to dictionary for API JSON responses.
        """
        res = dict(self.payload)
        res["message"] = self.message
        res["error_code"] = self.error_code
        return res


class ValidationException(BaseAppException):
    """
    Raised when input validation fails.
    """
    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=422, payload=payload, error_code="VALIDATION_ERROR")


class AuthenticationException(BaseAppException):
    """
    Raised when user authentication fails.
    """
    def __init__(self, message: str = "Authentication failed", payload: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=401, payload=payload, error_code="UNAUTHORIZED")


class AuthorizationException(BaseAppException):
    """
    Raised when user lacks permission to access resource.
    """
    def __init__(self, message: str = "Permission denied", payload: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=403, payload=payload, error_code="FORBIDDEN")


class NotFoundException(BaseAppException):
    """
    Raised when requested resource is not found.
    """
    def __init__(self, message: str = "Resource not found", payload: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=404, payload=payload, error_code="NOT_FOUND")


class ModelInferenceException(BaseAppException):
    """
    Raised when AI model prediction encounters failure.
    """
    def __init__(self, message: str = "Model inference failed", payload: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=500, payload=payload, error_code="MODEL_INFERENCE_ERROR")
