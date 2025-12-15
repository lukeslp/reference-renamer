"""
Logging utilities for Reference Renamer.
Provides enhanced logging setup with accessibility features.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    rich_console: bool = True,
) -> logging.Logger:
    """
    Creates a logger with enhanced formatting and accessibility features.

    Args:
        name: Logger name
        level: Logging level
        log_file: Optional file to log to
        rich_console: Whether to use rich console formatting

    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers = []

    # Create formatters
    console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    # Add console handler with rich formatting if requested
    if rich_console:
        console_handler = RichHandler(
            rich_tracebacks=True, markup=True, show_time=True, show_path=True
        )
        console_handler.setFormatter(logging.Formatter("%(message)s"))
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(console_format))

    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # Add file handler if requested
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(file_format))
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    return logger


class AccessibleFormatter(logging.Formatter):
    """
    Custom formatter that provides screen reader friendly output.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        # Add screen reader friendly markers
        level_marker = {
            logging.DEBUG: "Debug:",
            logging.INFO: "Info:",
            logging.WARNING: "Warning:",
            logging.ERROR: "Error:",
            logging.CRITICAL: "Critical:",
        }.get(record.levelno, "Log:")

        # Format the message
        formatted = super().format(record)

        # Add markers and structure
        structured = f"{level_marker} {formatted}"

        return structured


def setup_accessibility_logging(
    logger: logging.Logger, level: int = logging.INFO
) -> None:
    """
    Configures a logger with accessibility-focused formatting.

    Args:
        logger: Logger to configure
        level: Logging level
    """
    # Remove existing handlers
    logger.handlers = []

    # Create console handler with accessible formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        AccessibleFormatter("%(asctime)s - %(name)s - %(message)s")
    )
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # Set logger level
    logger.setLevel(level)
