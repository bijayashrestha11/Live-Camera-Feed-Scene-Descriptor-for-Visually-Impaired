"""
WebRTC data channel management.

Handles creation and communication via data channels.
"""

from typing import Callable, Optional

from aiortc import RTCDataChannel, RTCPeerConnection

from ..config import WEBRTC_CONST
from ..enums import DataChannelStatus
from ..utils.logging import get_logger
from ..utils.state import UseState

logger = get_logger(__name__)


class DataChannelManager:
    """
    Manages WebRTC data channel for sending captions.

    Provides state management and message sending capabilities.
    """

    def __init__(self, pc: RTCPeerConnection, channel_name: str = None):
        """
        Initialize the data channel manager.

        Args:
            pc: The peer connection to create channel on
            channel_name: Name for the data channel
        """
        channel_name = channel_name or WEBRTC_CONST.DATA_CHANNEL_NAME
        self._channel: RTCDataChannel = pc.createDataChannel(channel_name)
        self._status = DataChannelStatus.CLOSED

        # Set up event handlers
        self._setup_handlers()

        logger.debug(f"DataChannelManager initialized with channel: {channel_name}")

    def _setup_handlers(self) -> None:
        """Set up data channel event handlers."""

        @self._channel.on("open")
        def on_open():
            self._status = DataChannelStatus.OPEN
            logger.info("Data channel opened")

        @self._channel.on("close")
        def on_close():
            self._status = DataChannelStatus.CLOSED
            logger.info("Data channel closed")

        @self._channel.on("error")
        def on_error(error):
            self._status = DataChannelStatus.ERROR
            logger.error(f"Data channel error: {error}")

        @self._channel.on("message")
        def on_message(message):
            logger.debug(f"Received message: {message}")

    @property
    def status(self) -> DataChannelStatus:
        """Get the current channel status."""
        return self._status

    @property
    def is_open(self) -> bool:
        """Check if the channel is open."""
        return self._status == DataChannelStatus.OPEN

    @property
    def is_closed(self) -> bool:
        """Check if the channel is closed."""
        return self._status == DataChannelStatus.CLOSED

    def send(self, message: str) -> bool:
        """
        Send a message through the data channel.

        Args:
            message: The message to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_open:
            logger.warning("Cannot send message: channel not open")
            return False

        try:
            self._channel.send(message)
            logger.debug(f"Sent message: {message[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def send_caption(self, caption: str) -> bool:
        """
        Send a caption through the data channel.

        Args:
            caption: The caption text to send

        Returns:
            True if sent successfully, False otherwise
        """
        return self.send(caption)


def create_data_channel_manager(
    pc: RTCPeerConnection,
    channel_name: str = None
) -> DataChannelManager:
    """
    Create a new data channel manager.

    Args:
        pc: The peer connection
        channel_name: Optional channel name

    Returns:
        DataChannelManager instance
    """
    return DataChannelManager(pc, channel_name)
