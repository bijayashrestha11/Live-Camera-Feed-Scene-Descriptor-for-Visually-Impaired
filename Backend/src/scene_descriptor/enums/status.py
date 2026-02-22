"""
Status enumerations for Scene Descriptor.

Provides type-safe status values for various application components.
"""

import enum


class CapStatus(str, enum.Enum):
    """Caption generation status."""

    NEW_CAP = "NEW_CAP"      # New caption is available
    NO_CAP = "NO_CAP"        # No new caption available
    GENERATING = "GENERATING"  # Caption is being generated
    ERROR = "ERROR"          # Error during caption generation


class DataChannelStatus(str, enum.Enum):
    """WebRTC data channel status."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CONNECTING = "CONNECTING"
    ERROR = "ERROR"


class PeerConnectionStatus(str, enum.Enum):
    """WebRTC peer connection status."""

    NEW = "new"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    FAILED = "failed"
    CLOSED = "closed"


class ModelStatus(str, enum.Enum):
    """ML model status."""

    NOT_LOADED = "NOT_LOADED"
    LOADING = "LOADING"
    READY = "READY"
    PROCESSING = "PROCESSING"
    ERROR = "ERROR"


class ModelType(str, enum.Enum):
    """Available ML model types."""

    GIT = "git"              # Microsoft GIT-base-vatex model
    PULCHOWK = "pulchowk"    # Custom fine-tuned model
