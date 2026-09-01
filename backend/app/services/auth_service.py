"""
Authentication Service for User Registration and Login Management.
"""
import hashlib
import json
import os
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.security import generate_jwt_token
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AuthService:
    """
    Manages user registration (Sign Up) and user login with persistent JSON storage.
    """
    def __init__(self):
        self.users_file = os.path.join(settings.BASE_DIR, "data", "users.json")
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        if not os.path.exists(self.users_file):
            # Create default admin doctor account
            default_users = {
                "doctor@hospital.com": {
                    "email": "doctor@hospital.com",
                    "full_name": "Dr. Sarah Jenkins",
                    "role": "Physician",
                    "password_hash": self._hash_password("doctor123")
                }
            }
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(default_users, f, indent=4)

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _load_users(self) -> Dict[str, Any]:
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_users(self, users: Dict[str, Any]) -> None:
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)

    def register_user(self, email: str, password: str, full_name: str, role: str = "Doctor / Physician") -> Dict[str, Any]:
        email = email.strip().lower()
        if not email or not password:
            return {"success": False, "message": "Email and password are required."}

        users = self._load_users()
        if email in users:
            return {"success": False, "message": "User with this email already exists."}

        users[email] = {
            "email": email,
            "full_name": full_name,
            "role": role,
            "password_hash": self._hash_password(password)
        }
        self._save_users(users)
        logger.info(f"New user registered successfully: {email}")

        token = generate_jwt_token({"sub": email, "role": role})
        return {
            "success": True,
            "message": "Account created successfully!",
            "user": {"email": email, "full_name": full_name, "role": role},
            "token": token
        }

    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        email = email.strip().lower()
        users = self._load_users()
        user = users.get(email)

        if not user or user.get("password_hash") != self._hash_password(password):
            return {"success": False, "message": "Invalid email or password."}

        token = generate_jwt_token({"sub": email, "role": user.get("role")})
        logger.info(f"User logged in: {email}")
        return {
            "success": True,
            "message": "Login successful!",
            "user": {"email": email, "full_name": user.get("full_name"), "role": user.get("role")},
            "token": token
        }
