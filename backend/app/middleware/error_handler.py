"""
Global Error Handler Middleware for Flask.
"""
from flask import Flask, jsonify, Response
from werkzeug.exceptions import HTTPException
from app.core.exceptions import BaseAppException
from app.core.logging_config import get_logger
from app.utils.response import api_response

logger = get_logger(__name__)


def register_error_handlers(app: Flask) -> None:
    """
    Register global error handlers for custom exceptions and standard HTTP errors.
    """

    @app.errorhandler(BaseAppException)
    def handle_base_app_exception(error: BaseAppException):
        logger.warning(f"Application Exception [{error.error_code}]: {error.message}")
        return api_response(
            success=False,
            message=error.message,
            error=error.to_dict(),
            status_code=error.status_code
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        logger.warning(f"HTTP Exception [{error.code}]: {error.description}")
        return api_response(
            success=False,
            message=error.description or "HTTP Error",
            error={"error_code": f"HTTP_{error.code}", "status_code": error.code},
            status_code=error.code
        )

    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        logger.error(f"Unhandled Server Error: {str(error)}", exc_info=True)
        return api_response(
            success=False,
            message="An unexpected server error occurred",
            error={"error_code": "INTERNAL_SERVER_ERROR", "details": str(error)},
            status_code=500
        )
