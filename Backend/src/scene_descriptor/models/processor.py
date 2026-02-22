"""
Frame processing utilities for video captioning.

Provides functions for sampling and processing video frames.
"""

from typing import List, Optional

import av
import cv2
import numpy as np
from av import VideoFrame

from ..config import HP
from ..utils.logging import get_logger
from ..utils.exceptions import FrameProcessingError, FrameSamplingError, VideoReadError

logger = get_logger(__name__)


def sample_frame_indices(
    clip_len: int,
    seg_len: int,
    frame_sample_rate: int = 4
) -> np.ndarray:
    """
    Sample frame indices evenly across a video segment.

    Args:
        clip_len: Number of frames to sample
        seg_len: Total number of frames in segment
        frame_sample_rate: Sampling rate (unused, kept for compatibility)

    Returns:
        Array of frame indices to sample
    """
    if seg_len <= 0:
        raise FrameSamplingError(f"Invalid segment length: {seg_len}")

    if clip_len <= 0:
        raise FrameSamplingError(f"Invalid clip length: {clip_len}")

    indices = np.linspace(0, seg_len - 1, num=clip_len)
    indices = np.clip(indices, 0, seg_len - 1).astype(np.int64)

    logger.debug(f"Sampled {clip_len} indices from {seg_len} frames: {indices}")
    return indices


def sample_frames(
    frames: List[np.ndarray],
    num_samples: int = HP.CLIP_LENGTH
) -> np.ndarray:
    """
    Sample frames from a list of frames.

    Args:
        frames: List of frame arrays
        num_samples: Number of frames to sample

    Returns:
        Array of sampled frames

    Raises:
        FrameSamplingError: If sampling fails
    """
    if not frames:
        raise FrameSamplingError("Empty frame list provided")

    try:
        indices = sample_frame_indices(
            clip_len=num_samples,
            seg_len=len(frames)
        )
        frames_array = np.array(frames)
        return frames_array[indices]

    except Exception as e:
        raise FrameSamplingError(f"Failed to sample frames: {e}", cause=e)


def convert_frames_to_av(frames: np.ndarray) -> np.ndarray:
    """
    Convert numpy frames to AV VideoFrame format and back.

    This ensures consistent frame format for model processing.

    Args:
        frames: Array of frames (N, H, W, C) in RGB format

    Returns:
        Processed frames array

    Raises:
        FrameProcessingError: If conversion fails
    """
    try:
        converted = np.stack([
            av.VideoFrame.from_ndarray(frame, format="rgb24")
            .to_ndarray(format="rgb24")
            for frame in frames
        ])
        return converted

    except Exception as e:
        raise FrameProcessingError(f"Failed to convert frames: {e}", cause=e)


def read_video_frames(
    video_path: str,
    max_frames: Optional[int] = None
) -> List[np.ndarray]:
    """
    Read frames from a video file.

    Args:
        video_path: Path to the video file
        max_frames: Maximum number of frames to read (None = all frames)

    Returns:
        List of frame arrays

    Raises:
        VideoReadError: If video cannot be read
    """
    frames = []

    try:
        container = av.open(video_path)
        video_stream = container.streams.video[0]

        logger.debug(f"Reading video: {video_path}")
        logger.debug(f"Video duration: {video_stream.duration} frames")

        for i, frame in enumerate(container.decode(video=0)):
            if max_frames and i >= max_frames:
                break
            frames.append(frame.to_ndarray(format="rgb24"))

        container.close()
        logger.info(f"Read {len(frames)} frames from {video_path}")
        return frames

    except Exception as e:
        raise VideoReadError(f"Failed to read video {video_path}: {e}", cause=e)


def read_video_opencv(
    video_path: str,
    max_frames: Optional[int] = None
) -> List[np.ndarray]:
    """
    Read frames from a video file using OpenCV.

    Args:
        video_path: Path to the video file
        max_frames: Maximum number of frames to read (None = all frames)

    Returns:
        List of frame arrays (in RGB format)

    Raises:
        VideoReadError: If video cannot be read
    """
    frames = []

    try:
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise VideoReadError(f"Cannot open video: {video_path}")

        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if max_frames and frame_count >= max_frames:
                break

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
            frame_count += 1

        cap.release()
        logger.info(f"Read {len(frames)} frames from {video_path}")
        return frames

    except VideoReadError:
        raise
    except Exception as e:
        raise VideoReadError(f"Failed to read video {video_path}: {e}", cause=e)


def resize_frame(
    frame: np.ndarray,
    width: int,
    height: int
) -> np.ndarray:
    """
    Resize a frame to specified dimensions.

    Args:
        frame: Input frame array
        width: Target width
        height: Target height

    Returns:
        Resized frame
    """
    return cv2.resize(frame, (width, height))


def normalize_frames(frames: np.ndarray) -> np.ndarray:
    """
    Normalize frame pixel values to [0, 1] range.

    Args:
        frames: Input frames array

    Returns:
        Normalized frames
    """
    return frames.astype(np.float32) / 255.0
