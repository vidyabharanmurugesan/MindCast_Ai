"""
Standard Library Unittest Suite for Module 1: Core Backend Architecture.
"""
import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.core.config import settings
from app.core.exceptions import ValidationException, AuthenticationException
from app.core.security import generate_jwt_token, decode_jwt_token


class TestCoreBackend(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_health_check_endpoint(self):
        """
        Test GET /api/v1/health endpoint.
        """
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "healthy")
        self.assertIn("memory", data["data"])

    def test_jwt_token_operations(self):
        """
        Test JWT token encoding and decoding.
        """
        payload = {"uid": "user_789", "role": "clinician"}
        token = generate_jwt_token(payload, expires_in_minutes=30)
        self.assertIsInstance(token, str)
        
        decoded = decode_jwt_token(token)
        self.assertEqual(decoded["uid"], "user_789")
        self.assertEqual(decoded["role"], "clinician")

    def test_custom_exception(self):
        """
        Test ValidationException structure.
        """
        exc = ValidationException("Missing parameter")
        self.assertEqual(exc.status_code, 422)
        self.assertEqual(exc.error_code, "VALIDATION_ERROR")


if __name__ == "__main__":
    unittest.main()
