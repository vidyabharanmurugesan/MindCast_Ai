"""
Authentication REST API Routes.
"""
from flask import Blueprint, request
from app.services.auth_service import AuthService
from app.utils.response import api_response

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """
    User login endpoint.
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return api_response(success=False, data=None, message="Email and password are required", status_code=400)
        
    result = auth_service.login_user(email, password)
    if result["success"]:
        return api_response(success=True, data=result, message=result["message"])
    else:
        return api_response(success=False, data=None, message=result["message"], status_code=401)


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    """
    User registration endpoint.
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    
    if not email or not password or not full_name:
        return api_response(success=False, data=None, message="Email, password, and full name are required", status_code=400)
        
    result = auth_service.register_user(email, password, full_name)
    if result["success"]:
        return api_response(success=True, data=result, message=result["message"])
    else:
        return api_response(success=False, data=None, message=result["message"], status_code=400)
