"""
Structured Logging Infrastructure for Clinical AI Mental Health Assistant.
"""
import os
import sys
import warnings
import logging
from logging.handlers import RotatingFileHandler
from app.core.config import settings

# Suppress TensorFlow C++ CPU & deprecation warnings in terminal
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
warnings.filterwarnings("ignore")


def setup_logging() -> None:

    """
    Setup rotating file handler and console handler with structured formatting.
    """
    os.makedirs(settings.LOG_DIR, exist_ok=True)

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # File Handler
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Retrieve named logger.
    """
    return logging.getLogger(name)
