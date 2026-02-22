"""WebRTC module for Scene Descriptor."""

from .tracks import VideoCaptionTrack
from .connection import (
    create_peer_connection,
    remove_peer_connection,
    close_all_connections,
    get_connection_count,
    get_relay,
    create_media_player,
    create_media_recorder,
)
from .channels import DataChannelManager, create_data_channel_manager

__all__ = [
    "VideoCaptionTrack",
    "create_peer_connection",
    "remove_peer_connection",
    "close_all_connections",
    "get_connection_count",
    "get_relay",
    "create_media_player",
    "create_media_recorder",
    "DataChannelManager",
    "create_data_channel_manager",
]
