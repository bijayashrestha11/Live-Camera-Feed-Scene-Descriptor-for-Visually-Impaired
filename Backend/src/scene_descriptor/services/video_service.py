"""
Video processing service.

Handles video file operations and frame extraction.
"""

import os
from pathlib import Path
from typing import List, Optional, Generator

import numpy as np

from ..models import read_video_frames, read_video_opencv, sample_frames
from ..config import settings, HP
from ..utils.logging import get_logger
from ..utils.exceptions import VideoReadError

logger = get_logger(__name__)


class VideoService:
    """
    Service for video file operations.

    Provides methods for reading videos, extracting frames,
    and batch processing video directories.
    """

    def __init__(self):
        """Initialize the video service."""
        logger.debug("VideoService initialized")

    def read_video(
        self,
        video_path: str,
        max_frames: Optional[int] = None,
        use_opencv: bool = False
    ) -> List[np.ndarray]:
        """
        Read frames from a video file.

        Args:
            video_path: Path to the video file
            max_frames: Maximum number of frames to read
            use_opencv: Use OpenCV instead of PyAV

        Returns:
            List of frame arrays

        Raises:
            VideoReadError: If video cannot be read
        """
        if not os.path.exists(video_path):
            raise VideoReadError(f"Video file not found: {video_path}")

        logger.info(f"Reading video: {video_path}")

        if use_opencv:
            return read_video_opencv(video_path, max_frames)
        return read_video_frames(video_path, max_frames)

    def get_sampled_frames(
        self,
        video_path: str,
        num_samples: int = None
    ) -> np.ndarray:
        """
        Read and sample frames from a video.

        Args:
            video_path: Path to the video file
            num_samples: Number of frames to sample

        Returns:
            Array of sampled frames

        Raises:
            VideoReadError: If video cannot be read
        """
        num_samples = num_samples or HP.CLIP_LENGTH
        frames = self.read_video(video_path)
        return sample_frames(frames, num_samples)

    def list_videos(
        self,
        directory: str,
        extensions: List[str] = None
    ) -> List[Path]:
        """
        List all video files in a directory.

        Args:
            directory: Directory to search
            extensions: List of video extensions to include

        Returns:
            List of video file paths
        """
        extensions = extensions or [".mp4", ".avi", ".mov", ".mkv", ".webm"]
        directory = Path(directory)

        if not directory.exists():
            logger.warning(f"Directory not found: {directory}")
            return []

        videos = []
        for ext in extensions:
            videos.extend(directory.glob(f"*{ext}"))
            videos.extend(directory.glob(f"*{ext.upper()}"))

        logger.info(f"Found {len(videos)} videos in {directory}")
        return sorted(videos)

    def process_video_batch(
        self,
        directory: str,
        num_samples: int = None
    ) -> Generator[tuple, None, None]:
        """
        Process all videos in a directory.

        Yields tuples of (video_path, sampled_frames).

        Args:
            directory: Directory containing videos
            num_samples: Number of frames to sample per video

        Yields:
            Tuple of (video_path, frames_array)
        """
        videos = self.list_videos(directory)

        for video_path in videos:
            try:
                frames = self.get_sampled_frames(str(video_path), num_samples)
                yield str(video_path), frames
            except VideoReadError as e:
                logger.error(f"Failed to process {video_path}: {e}")
                continue


# Singleton instance
_video_service: Optional[VideoService] = None


def get_video_service() -> VideoService:
    """Get the video service singleton."""
    global _video_service
    if _video_service is None:
        _video_service = VideoService()
    return _video_service
