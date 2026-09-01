"""
AI Mental Health Assistant Backend Package.
"""
from typing import Tuple, Dict, Any
from flask import Flask
from flask_cors import CORS
from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.middleware.error_handler import register_error_handlers
from app.api.v1.health_routes import health_bp
from app.api.v1.dataset_routes import dataset_bp
from app.api.v1.model_routes import model_bp
from app.api.v1.clinical_routes import clinical_bp
from app.api.v1.auth_routes import auth_bp

logger = get_logger(__name__)


def create_app(config_object: Any = None) -> Flask:
    """
    Application Factory for Flask AI Mental Health Assistant Backend.
    
    Args:
        config_object: Optional configuration object to override defaults.
        
    Returns:
        Flask: Configured Flask application instance.
    """
    setup_logging()
    app = Flask(__name__)
    
    # Load configuration
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["ENV"] = settings.FLASK_ENV
    app.config["DEBUG"] = settings.DEBUG
    
    if config_object:
        app.config.from_object(config_object)
        
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register Blueprints
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(dataset_bp, url_prefix="/api/v1")
    app.register_blueprint(model_bp, url_prefix="/api/v1")
    app.register_blueprint(clinical_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1")
    
    logger.info("AI Mental Health Assistant Backend Application Initialized Successfully")
    return app



