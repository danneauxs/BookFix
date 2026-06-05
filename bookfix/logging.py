"""
Logging configuration for Bookfix.

This module sets up logging for the Bookfix application with both file and console output.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(log_level: str = "DEBUG", log_to_file: bool = True) -> None:
    """
    Set up logging configuration for Bookfix.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to a file in addition to console
    """
    # Log to the project root directory
    log_dir = Path(__file__).parent.parent

    # Set up logging format
    log_format = "[%(asctime)s] [%(levelname)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Get root logger and remove existing handlers to avoid duplication
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Configure root logger
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(console_handler)

    # File handler (if enabled)
    if log_to_file:
        log_file = log_dir / "bookfix_ai_debug.log"
        # Use 'w' mode to clear the log on each run
        file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        root_logger.addHandler(file_handler)

        # Full execution log in logs/ directory
        logs_dir = log_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        execution_log = logs_dir / "bookfix_execution.log"
        # Use 'w' mode to overwrite (fresh per run)
        execution_handler = logging.FileHandler(
            execution_log, mode="w", encoding="utf-8"
        )
        execution_handler.setFormatter(logging.Formatter(log_format, date_format))
        root_logger.addHandler(execution_handler)


def log_message(message: str, level: str = "INFO") -> None:
    """
    Log a message with the specified level.

    Args:
        message: The message to log
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger("bookfix")

    level_map = {
        "DEBUG": logger.debug,
        "INFO": logger.info,
        "WARNING": logger.warning,
        "ERROR": logger.error,
        "CRITICAL": logger.critical,
    }

    log_func = level_map.get(level.upper(), logger.info)
    log_func(message)


def log_processing_start(file_path: str) -> None:
    """Log the start of processing a file."""
    log_message(f"Starting processing of file: {file_path}")


def log_processing_complete(file_path: str, changes_count: int) -> None:
    """Log the completion of processing a file."""
    log_message(
        f"Completed processing of file: {file_path} ({changes_count} changes made)"
    )


def log_error(error: Exception, context: str = "") -> None:
    """Log an error with context information."""
    error_msg = (
        f"Error in {context}: {str(error)}" if context else f"Error: {str(error)}"
    )
    log_message(error_msg, level="ERROR")


def log_debug(message: str) -> None:
    """Log a debug message."""
    log_message(message, level="DEBUG")


def log_warning(message: str) -> None:
    """Log a warning message."""
    log_message(message, level="WARNING")
