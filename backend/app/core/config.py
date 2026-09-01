"""
Centralized Configuration Settings using Pydantic BaseSettings or Dataclasses.
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """
    Application Settings container parsing environment variables with safe defaults.
    """
    PORT: int = int(os.getenv("PORT", "5000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-production-key-mental-health-ai")

    # Firebase Config
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "backend/config/firebase-credentials.json")
    FIREBASE_STORAGE_BUCKET: str = os.getenv("FIREBASE_STORAGE_BUCKET", "mental-health-ai.appspot.com")

    # Directory Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MODEL_DIR: str = os.path.join(BASE_DIR, "models", "saved")
    DATASET_DIR: str = os.path.join(BASE_DIR, "sample_datasets")
    LOG_DIR: str = os.path.join(BASE_DIR, "logs")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.path.join(LOG_DIR, "app.log")


settings = Settings()
