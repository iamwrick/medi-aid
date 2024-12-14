# src/utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from src.config.settings import LOG_DIR, LOG_LEVEL


def get_logger(name: str) -> logging.Logger:
    """
    Create a logger with both file and console handlers.
    """
    # Create logs directory if it doesn't exist
    LOG_DIR.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # Prevent adding handlers multiple times
    if not logger.handlers:
        # File handler
        file_handler = RotatingFileHandler(
            LOG_DIR / f"{name}.log",
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(
                '%(levelname)s - %(message)s'
            )
        )
        logger.addHandler(console_handler)

    return logger