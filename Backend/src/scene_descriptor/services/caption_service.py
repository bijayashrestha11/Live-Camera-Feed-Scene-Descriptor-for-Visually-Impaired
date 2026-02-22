"""
Caption generation service.

Provides high-level interface for generating captions from video frames.
"""

from typing import List, Optional

import numpy as np

from ..models import get_model_manager, sample_frames, convert_frames_to_av
from ..config import settings
from ..utils.logging import get_logger
from ..utils.exceptions import ModelInferenceError, FrameProcessingError

logger = get_logger(__name__)


class CaptionService:
    """
    Service for generating captions from video frames.

    Provides a clean interface for caption generation,
    handling frame processing and model inference.
    """

    def __init__(self):
        """Initialize the caption service."""
        self._model_manager = get_model_manager()
        logger.debug("CaptionService initialized")

    def generate_caption_from_frames(
        self,
        frames: List[np.ndarray],
        num_samples: int = None
    ) -> str:
        """
        Generate a caption from a list of video frames.

        Args:
            frames: List of frame arrays (H, W, C format)
            num_samples: Number of frames to sample (default from config)

        Returns:
            Generated caption string

        Raises:
            FrameProcessingError: If frame processing fails
            ModelInferenceError: If caption generation fails
        """
        if not frames:
            raise FrameProcessingError("No frames provided")

        num_samples = num_samples or settings.num_sample_frames

        try:
            logger.info(f"Generating caption from {len(frames)} frames")

            # Sample frames
            sampled = sample_frames(frames, num_samples)
            logger.debug(f"Sampled {len(sampled)} frames")

            # Convert to AV format
            converted = convert_frames_to_av(sampled)

            # Preprocess for model
            pixel_values = self._model_manager.preprocess_frames(converted)

            # Generate caption
            caption = self._model_manager.generate_caption(pixel_values)

            logger.info(f"Generated caption: {caption}")
            return caption

        except ModelInferenceError:
            raise
        except Exception as e:
            raise FrameProcessingError(f"Failed to process frames: {e}", cause=e)

    def is_ready(self) -> bool:
        """Check if the service is ready for caption generation."""
        return self._model_manager.is_ready()


# Singleton instance
_caption_service: Optional[CaptionService] = None


def get_caption_service() -> CaptionService:
    """Get the caption service singleton."""
    global _caption_service
    if _caption_service is None:
        _caption_service = CaptionService()
    return _caption_service
