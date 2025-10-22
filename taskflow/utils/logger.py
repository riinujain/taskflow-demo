"""Centralized logging configuration."""

import logging
import sys
from typing import Optional

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name.

    This is the recommended way to get loggers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger


# Module-level logger instance
logger = get_logger(__name__)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Setup a custom logger with specific configuration.

    This is an alternative pattern that some modules use instead of get_logger.
    Creates inconsistency in logging approach.
    """
    custom_logger = logging.getLogger(name)
    custom_logger.setLevel(level)

    # Add handler if not already present
    if not custom_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        custom_logger.addHandler(handler)

    return custom_logger


def log_info(message: str, logger_name: Optional[str] = None):
    """Log an info message.

    Yet another way to log messages, adding to the inconsistency.
    """
    log = logging.getLogger(logger_name) if logger_name else logger
    log.info(message)


def log_error(message: str, logger_name: Optional[str] = None):
    """Log an error message."""
    log = logging.getLogger(logger_name) if logger_name else logger
    log.error(message)
