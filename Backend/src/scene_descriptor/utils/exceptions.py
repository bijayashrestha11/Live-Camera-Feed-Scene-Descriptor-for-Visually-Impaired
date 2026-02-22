"""
Custom exception hierarchy for Scene Descriptor.

All exceptions auto-log on creation for easier debugging.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SceneDescriptorError(Exception):
    """
    Base exception for all application errors.

    Automatically logs the error when raised.
    """

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.cause = cause
        # Auto-log on creation
        if cause:
            logger.error(
                f"{self.__class__.__name__}: {message}",
                exc_info=cause
            )
        else:
            logger.error(f"{self.__class__.__name__}: {message}")

    def __str__(self) -> str:
        if self.cause:
            return f"{self.message} (caused by: {self.cause})"
        return self.message


# =============================================================================
# Model Errors
# =============================================================================

class ModelError(SceneDescriptorError):
    """Base class for ML model related errors."""
    pass


class ModelLoadError(ModelError):
    """Failed to load ML model from disk or HuggingFace."""
    pass


class ModelInferenceError(ModelError):
    """Error during model inference/caption generation."""
    pass


class ModelNotFoundError(ModelError):
    """Requested model does not exist."""
    pass


class ModelNotInitializedError(ModelError):
    """Model was accessed before initialization."""
    pass


# =============================================================================
# WebRTC Errors
# =============================================================================

class WebRTCError(SceneDescriptorError):
    """Base class for WebRTC related errors."""
    pass


class ConnectionError(WebRTCError):
    """Failed to establish or maintain WebRTC connection."""
    pass


class ConnectionClosed(WebRTCError):
    """WebRTC connection was closed unexpectedly."""
    pass


class DataChannelError(WebRTCError):
    """Error with data channel communication."""
    pass


class SDPError(WebRTCError):
    """Error parsing or creating SDP offer/answer."""
    pass


# =============================================================================
# Video Processing Errors
# =============================================================================

class VideoProcessingError(SceneDescriptorError):
    """Base class for video processing errors."""
    pass


class FrameProcessingError(VideoProcessingError):
    """Error processing video frames."""
    pass


class FrameSamplingError(VideoProcessingError):
    """Error sampling frames from video."""
    pass


class VideoReadError(VideoProcessingError):
    """Error reading video file."""
    pass


# =============================================================================
# Configuration Errors
# =============================================================================

class ConfigurationError(SceneDescriptorError):
    """Invalid or missing configuration."""
    pass


class EnvironmentError(ConfigurationError):
    """Missing or invalid environment variable."""
    pass


# =============================================================================
# API Errors
# =============================================================================

class APIError(SceneDescriptorError):
    """Base class for API-related errors."""
    pass


class ValidationError(APIError):
    """Request validation failed."""
    pass


class RequestError(APIError):
    """Error processing API request."""
    pass
