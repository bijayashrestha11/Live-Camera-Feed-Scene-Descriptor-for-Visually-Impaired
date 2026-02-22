"""
Video track handler for WebRTC streams.

Processes video frames from WebRTC connections and generates captions.
"""

import time
from threading import Thread
from typing import Callable, List, Optional

import av
import numpy as np
from aiortc import MediaStreamTrack
from aiortc.mediastreams import MediaStreamError

from ..config import HP, settings
from ..enums import CapStatus
from ..models import get_model_manager, sample_frames, convert_frames_to_av
from ..utils.logging import get_logger
from ..utils.exceptions import FrameProcessingError

logger = get_logger(__name__)


class VideoCaptionTrack:
    """
    Video stream track that processes frames and generates captions.

    Collects frames for a configurable duration, samples them,
    and runs ML inference in a background thread.
    """

    def __init__(self, track: MediaStreamTrack):
        """
        Initialize the video caption track.

        Args:
            track: The WebRTC media stream track to process
        """
        self._track: MediaStreamTrack = track
        self._model_manager = get_model_manager()

        # Frame collection
        self._frames: List[np.ndarray] = []
        self._count: int = 0

        # Timing
        self._start_time: float = time.time()
        self._is_receiving: bool = False

        # Caption state
        self._caption: str = ""

        logger.debug("VideoCaptionTrack initialized")

    @property
    def caption(self) -> str:
        """Get the most recently generated caption."""
        return self._caption

    def _sample_indices(
        self,
        clip_len: int,
        seg_len: int,
        frame_sample_rate: int = 4
    ) -> np.ndarray:
        """
        Sample frame indices evenly across the collected frames.

        Args:
            clip_len: Number of frames to sample
            seg_len: Total number of frames available
            frame_sample_rate: Sampling rate (unused, kept for compatibility)

        Returns:
            Array of indices to sample
        """
        indices = np.linspace(0, seg_len - 1, num=clip_len)
        indices = np.clip(indices, 0, seg_len - 1).astype(np.int64)
        return indices

    def _sample_frames(self, frames: List[np.ndarray]) -> np.ndarray:
        """
        Sample frames from the collected frame list.

        Args:
            frames: List of frame arrays

        Returns:
            Array of sampled frames
        """
        indices = self._sample_indices(
            clip_len=HP.CLIP_LENGTH,
            seg_len=len(frames)
        )
        logger.debug(f"Sampling {HP.CLIP_LENGTH} frames from {len(frames)} total")
        return np.array(frames)[indices]

    def _predict_caption(
        self,
        pixel_values: np.ndarray,
        set_caption_state: Callable[[CapStatus], None]
    ) -> None:
        """
        Generate caption in a background thread.

        Args:
            pixel_values: Preprocessed frame tensor
            set_caption_state: Callback to update caption state
        """
        try:
            caption = self._model_manager.generate_caption(pixel_values)
            self._caption = caption
            logger.info(f"Caption generated: {caption}")
            set_caption_state(CapStatus.NEW_CAP)

        except Exception as e:
            logger.error(f"Caption generation failed: {e}", exc_info=True)
            set_caption_state(CapStatus.ERROR)

    async def receive(self, set_caption_state: Callable[[CapStatus], None]) -> None:
        """
        Receive and process video frames.

        Collects frames for the configured duration, then processes
        them and generates a caption.

        Args:
            set_caption_state: Callback to update caption state
        """
        elapsed = time.time() - self._start_time

        if elapsed <= settings.frame_capture_seconds:
            # Still collecting frames
            try:
                frame = await self._track.recv()

                # Update start time on first frame
                if not self._is_receiving:
                    self._start_time = time.time()
                    self._is_receiving = True
                    logger.debug("Started receiving frames")

                self._count += 1

                # Convert frame to numpy array
                img: np.ndarray = frame.to_ndarray(format="rgb24")
                self._frames.append(img)

            except MediaStreamError as e:
                logger.warning(f"Media stream error: {e}")
                return

        else:
            # Time to process collected frames
            if not self._frames:
                logger.warning("No frames collected, skipping processing")
                self._reset()
                return

            logger.info(f"Processing {len(self._frames)} frames")

            try:
                # Sample frames
                sampled_frames = self._sample_frames(self._frames)

                # Convert to AV format
                processed_frames = convert_frames_to_av(sampled_frames)

                # Preprocess for model
                pixel_values = self._model_manager.preprocess_frames(processed_frames)

                # Start inference in background thread
                logger.debug("Starting caption generation thread")
                thread = Thread(
                    target=self._predict_caption,
                    args=(pixel_values, set_caption_state)
                )
                thread.start()

            except Exception as e:
                logger.error(f"Frame processing failed: {e}", exc_info=True)
                set_caption_state(CapStatus.ERROR)

            # Reset for next batch
            self._reset()

    def _reset(self) -> None:
        """Reset frame collection for the next batch."""
        self._count = 0
        self._frames = []
        self._start_time = time.time()
        logger.debug("Frame collection reset")
