"""Utility modules for Scene Descriptor."""

from .logging import setup_logging, get_logger
from .state import UseState, StateManager
from .exceptions import (
    SceneDescriptorError,
    ModelError,
    ModelLoadError,
    ModelInferenceError,
    ModelNotFoundError,
    ModelNotInitializedError,
    WebRTCError,
    ConnectionError,
    ConnectionClosed,
    DataChannelError,
    SDPError,
    VideoProcessingError,
    FrameProcessingError,
    FrameSamplingError,
    VideoReadError,
    ConfigurationError,
    EnvironmentError,
    APIError,
    ValidationError,
    RequestError,
)

__all__ = [
    # Logging
    "setup_logging",
    "get_logger",
    # State
    "UseState",
    "StateManager",
    # Exceptions
    "SceneDescriptorError",
    "ModelError",
    "ModelLoadError",
    "ModelInferenceError",
    "ModelNotFoundError",
    "ModelNotInitializedError",
    "WebRTCError",
    "ConnectionError",
    "ConnectionClosed",
    "DataChannelError",
    "SDPError",
    "VideoProcessingError",
    "FrameProcessingError",
    "FrameSamplingError",
    "VideoReadError",
    "ConfigurationError",
    "EnvironmentError",
    "APIError",
    "ValidationError",
    "RequestError",
]
