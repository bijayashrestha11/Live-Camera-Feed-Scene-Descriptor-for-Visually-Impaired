"""
Scene Descriptor - Real-time video captioning for visually impaired users.

A WebRTC-based application that uses ML models to generate captions
from live camera feeds in real-time.
"""

__version__ = "1.0.0"
__author__ = "Bijaya Shrestha"

from .config.settings import settings
from .utils.logging import setup_logging, get_logger

__all__ = [
    "settings",
    "setup_logging",
    "get_logger",
    "__version__",
]
