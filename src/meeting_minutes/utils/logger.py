"""
Logging configuration for Meeting Minutes Agent.
"""

import logging
from pathlib import Path
from typing import Optional

from ..config.app_config import LOGGING_CONFIG


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with file and console handlers.

    Args:
        name: Logger name
        level: Optional log level override

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Set log level
    log_level = level or LOGGING_CONFIG["level"]
    logger.setLevel(getattr(logging, log_level.upper()))

    # Create formatter
    formatter = logging.Formatter(LOGGING_CONFIG["format"])

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (create directory if needed)
    log_file_path = Path(LOGGING_CONFIG["file_path"])
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Create default logger
default_logger = setup_logger("meeting_minutes")
