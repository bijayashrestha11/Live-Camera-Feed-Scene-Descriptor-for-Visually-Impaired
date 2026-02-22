"""
API request handlers for Scene Descriptor.

Contains the main endpoint handlers for WebRTC signaling and model management.
"""

import json
import os

from aiohttp import web

from ..config import settings, WEBRTC_CONST
from ..enums import CapStatus, DataChannelStatus, PeerConnectionStatus, ModelType
from ..models import get_model_manager
from ..webrtc import (
    VideoCaptionTrack,
    create_peer_connection,
    remove_peer_connection,
    create_media_player,
    create_media_recorder,
)
from ..utils.logging import get_logger
from ..utils.state import UseState
from ..utils.exceptions import WebRTCError, SDPError, ModelNotFoundError

logger = get_logger(__name__)

# Application state
_data_channel_state, _set_data_channel_state = UseState(DataChannelStatus.CLOSED).init()
_caption_state, _set_caption_state = UseState(CapStatus.NO_CAP).init()


async def offer_handler(request: web.Request) -> web.Response:
    """
    Handle WebRTC offer from client.

    Creates a peer connection, sets up media handling,
    and returns the SDP answer.

    Args:
        request: The incoming HTTP request with SDP offer

    Returns:
        JSON response with SDP answer
    """
    try:
        logger.info("Received WebRTC offer request")
        params = await request.json()

        # Validate request
        if "sdp" not in params or "type" not in params:
            logger.warning("Invalid offer: missing sdp or type")
            return web.json_response(
                {"error": "Missing sdp or type in request"},
                status=400
            )

        from aiortc import RTCSessionDescription
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

        # Create peer connection
        pc, pc_id = create_peer_connection()
        logger.info(f"Created peer connection: {pc_id}")

        # Create data channel for sending captions
        channel = pc.createDataChannel(WEBRTC_CONST.DATA_CHANNEL_NAME)

        @channel.on("open")
        def on_channel_open():
            logger.info("Data channel opened")
            _set_data_channel_state(DataChannelStatus.OPEN)

        @channel.on("close")
        def on_channel_close():
            logger.info("Data channel closed")
            _set_data_channel_state(DataChannelStatus.CLOSED)

        # Prepare media
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        audio_path = os.path.join(root_dir, WEBRTC_CONST.AUDIO_FILE)

        player = None
        if os.path.exists(audio_path):
            player = create_media_player(audio_path)
        recorder = create_media_recorder()

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            logger.info(f"Connection state: {pc.connectionState}")
            if pc.connectionState == "failed":
                await pc.close()
                remove_peer_connection(pc)

        @pc.on("track")
        async def on_track(track):
            logger.info(f"Track received: {track.kind}")

            if track.kind == "audio" and player:
                pc.addTrack(player.audio)
                recorder.addTrack(track)
            elif track.kind == "video":
                logger.info("Video track added, starting caption processing")
                video_track = VideoCaptionTrack(track)

                while True:
                    # Check if connection should stop
                    if (pc.connectionState == PeerConnectionStatus.CONNECTED and
                            _data_channel_state == DataChannelStatus.CLOSED):
                        logger.info("Connection closed, stopping video processing")
                        break

                    # Receive and process frames
                    await video_track.receive(_set_caption_state)

                    # Send caption if new one is available
                    if _caption_state == CapStatus.NEW_CAP:
                        _set_caption_state(CapStatus.NO_CAP)
                        caption = video_track.caption
                        if caption:
                            channel.send(caption)
                            logger.debug(f"Sent caption: {caption[:50]}...")

            @track.on("ended")
            async def on_track_ended():
                logger.info(f"Track {track.kind} ended")
                await recorder.stop()

        # Process offer and create answer
        await pc.setRemoteDescription(offer)
        await recorder.start()

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        logger.info("Successfully created answer")
        return web.json_response({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request: {e}")
        return web.json_response({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error handling offer: {e}", exc_info=True)
        return web.json_response({"error": str(e)}, status=500)


async def change_model_handler(request: web.Request) -> web.Response:
    """
    Handle model switching request.

    Args:
        request: The incoming HTTP request with model name

    Returns:
        JSON response with the changed model name
    """
    try:
        logger.info("Received change model request")
        params = await request.json()

        if "model" not in params:
            logger.warning("Invalid request: missing model parameter")
            return web.json_response(
                {"error": "Missing model parameter"},
                status=400
            )

        model_name = params["model"].lower()
        model_manager = get_model_manager()

        try:
            if model_name == "pulchowk":
                changed = model_manager.switch_model(ModelType.PULCHOWK)
            elif model_name == "git":
                changed = model_manager.switch_model(ModelType.GIT)
            else:
                return web.json_response(
                    {"error": f"Unknown model: {model_name}"},
                    status=400
                )

            logger.info(f"Model changed to: {changed}")
            return web.json_response({"changed_model": changed})

        except ModelNotFoundError as e:
            logger.warning(f"Model not found: {e}")
            return web.json_response(
                {"error": str(e), "changed_model": "NO CHANGE"},
                status=404
            )

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request: {e}")
        return web.json_response({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error changing model: {e}", exc_info=True)
        return web.json_response({"error": str(e)}, status=500)


async def health_handler(request: web.Request) -> web.Response:
    """
    Health check endpoint.

    Returns:
        JSON response with health status
    """
    model_manager = get_model_manager()
    return web.json_response({
        "status": "healthy",
        "model_ready": model_manager.is_ready(),
        "current_model": model_manager.current_model_type.value if model_manager.is_ready() else None
    })
