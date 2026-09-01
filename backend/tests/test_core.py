"""
Unit & Integration Tests for Module 1: Core Backend Architecture.
"""
import pytest
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.core.config import settings
from app.core.exceptions import ValidationException, AuthenticationException
from app.core.security import generate_jwt_token, decode_jwt_token


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check_endpoint(client):
    """
    Test GET /api/v1/health endpoint returns 200 OK and expected structure.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "data" in json_data
    assert json_data["data"]["status"] == "healthy"
    assert "memory" in json_data["data"]


def test_jwt_token_generation_and_decoding():
    """
    Test JWT token generation and validation.
    """
    payload = {"uid": "test_user_123", "role": "patient"}
    token = generate_jwt_token(payload, expires_in_minutes=15)
    assert isinstance(token, str)
    
    decoded = decode_jwt_token(token)
    assert decoded["uid"] == "test_user_123"
    assert decoded["role"] == "patient"


def test_custom_exception_handling(client):
    """
    Test custom exceptions and error response formatting.
    """
    exc = ValidationException("Test validation error")
    assert exc.status_code == 422
    assert exc.error_code == "VALIDATION_ERROR"
    assert exc.to_dict()["message"] == "Test validation error"
