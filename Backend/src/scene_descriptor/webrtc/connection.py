"""
WebRTC peer connection management.

Handles creation and lifecycle of peer connections.
"""

import uuid
from typing import Set, Optional

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRelay

from ..config import settings, WEBRTC_CONST
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Global connection tracking
_peer_connections: Set[RTCPeerConnection] = set()
_relay: Optional[MediaRelay] = None


def get_relay() -> MediaRelay:
    """Get or create the media relay singleton."""
    global _relay
    if _relay is None:
        _relay = MediaRelay()
    return _relay


def create_peer_connection() -> tuple[RTCPeerConnection, str]:
    """
    Create a new RTCPeerConnection.

    Returns:
        Tuple of (peer_connection, connection_id)
    """
    pc = RTCPeerConnection()
    pc_id = f"PeerConnection({uuid.uuid4()})"

    _peer_connections.add(pc)
    logger.info(f"Created peer connection: {pc_id}")

    return pc, pc_id


def remove_peer_connection(pc: RTCPeerConnection) -> None:
    """
    Remove a peer connection from tracking.

    Args:
        pc: The peer connection to remove
    """
    _peer_connections.discard(pc)
    logger.debug(f"Removed peer connection, {len(_peer_connections)} remaining")


async def close_all_connections() -> None:
    """Close all tracked peer connections."""
    logger.info(f"Closing {len(_peer_connections)} peer connections")

    for pc in list(_peer_connections):
        try:
            await pc.close()
        except Exception as e:
            logger.warning(f"Error closing peer connection: {e}")

    _peer_connections.clear()
    logger.info("All peer connections closed")


def get_connection_count() -> int:
    """Get the number of active peer connections."""
    return len(_peer_connections)


def create_media_player(audio_file: str) -> MediaPlayer:
    """
    Create a media player for audio playback.

    Args:
        audio_file: Path to the audio file

    Returns:
        MediaPlayer instance
    """
    return MediaPlayer(audio_file)


def create_media_recorder() -> MediaBlackhole:
    """
    Create a media recorder (blackhole for now).

    Returns:
        MediaBlackhole instance
    """
    return MediaBlackhole()
