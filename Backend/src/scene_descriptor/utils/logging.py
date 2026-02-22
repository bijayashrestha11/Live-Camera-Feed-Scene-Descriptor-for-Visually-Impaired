"""
Logging configuration for Scene Descriptor.

Provides rotating file handlers, colored console output, and module-specific loggers.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to log levels for console output."""

    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    console_output: bool = True,
    app_name: str = "scene_descriptor"
) -> logging.Logger:
    """
    Configure application-wide logging.

    Features:
    - Colored console output
    - Rotating file handler (10MB max, 5 backups)
    - Separate error-only log file
    - Reduced noise from third-party libraries

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files. If None, file logging is disabled.
        console_output: Whether to output to console
        app_name: Application name for the root logger

    Returns:
        Configured root logger
    """
    # Create log directory if specified
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

    # Create formatters
    detailed_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    detailed_formatter = logging.Formatter(detailed_format, datefmt=date_format)
    colored_formatter = ColoredFormatter(detailed_format, datefmt=date_format)

    error_format = (
        "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d\n"
        "Message: %(message)s\n"
        + "-" * 80
    )
    error_formatter = logging.Formatter(error_format, datefmt=date_format)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler with colors
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(colored_formatter)
        console_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)

    # File handlers (only if log_dir is specified)
    if log_dir:
        # Main rotating file handler (10MB, 5 backups)
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)

        # Error-only file handler
        error_handler = RotatingFileHandler(
            log_dir / "error.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setFormatter(error_formatter)
        error_handler.setLevel(logging.ERROR)
        root_logger.addHandler(error_handler)

        # WebRTC-specific log
        webrtc_handler = RotatingFileHandler(
            log_dir / "webrtc.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        webrtc_handler.setFormatter(detailed_formatter)
        webrtc_handler.setLevel(logging.DEBUG)
        webrtc_logger = logging.getLogger("webrtc")
        webrtc_logger.addHandler(webrtc_handler)

        # Model-specific log
        model_handler = RotatingFileHandler(
            log_dir / "model.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        model_handler.setFormatter(detailed_formatter)
        model_handler.setLevel(logging.DEBUG)
        model_logger = logging.getLogger("models")
        model_logger.addHandler(model_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("aiortc").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance for the module
    """
    return logging.getLogger(name)
