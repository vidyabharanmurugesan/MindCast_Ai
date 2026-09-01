"""
System & AI Model Health REST API Routes.
"""
import sys
from flask import Blueprint
from app.utils.response import api_response
from app.core.config import settings

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def get_health_status():
    """
    Get system health status, memory usage, environment configuration, and active services.
    """
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_info = {
            "total_mb": round(memory.total / (1024 * 1024), 2),
            "available_mb": round(memory.available / (1024 * 1024), 2),
            "percent_used": memory.percent
        }
    except ImportError:
        memory_info = {
            "total_mb": 0.0,
            "available_mb": 0.0,
            "percent_used": 0.0,
            "note": "psutil module not installed"
        }

    health_data = {
        "status": "healthy",
        "app_name": "AI Mental Health Assistant Backend",
        "environment": settings.FLASK_ENV,
        "python_version": sys.version.split()[0],
        "memory": memory_info
    }
    return api_response(success=True, data=health_data, message="System is operational")

