#!/usr/bin/env python3
"""
Batch Video Captioning Script

Generate captions for video files using the Scene Descriptor ML models.

Usage:
    Single video:
        python -m scripts.batch_caption --input video.mp4

    Batch processing:
        python -m scripts.batch_caption --input videos/ --output captions.csv

    With specific model:
        python -m scripts.batch_caption --input video.mp4 --model pulchowk
"""

import argparse
import csv
import os
import sys
import time
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scene_descriptor.config import settings, HP
from scene_descriptor.models import get_model_manager, read_video_frames, sample_frames, convert_frames_to_av
from scene_descriptor.enums import ModelType
from scene_descriptor.utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate captions for video files"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input video file or directory"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output CSV file (default: captions.csv)"
    )
    parser.add_argument(
        "--model", "-m",
        choices=["git", "pulchowk"],
        default="git",
        help="Model to use for captioning (default: git)"
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=settings.model_dir,
        help=f"Directory containing ML models (default: {settings.model_dir})"
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=50,
        help="Maximum caption length (default: 50)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--save-frames",
        action="store_true",
        help="Save sampled frames to disk"
    )
    parser.add_argument(
        "--frames-dir",
        type=Path,
        default=Path("frames"),
        help="Directory to save frames (default: frames/)"
    )

    return parser.parse_args()


def get_video_files(input_path: str) -> List[Path]:
    """
    Get list of video files from input path.

    Args:
        input_path: Path to video file or directory

    Returns:
        List of video file paths
    """
    input_path = Path(input_path)
    extensions = [".mp4", ".avi", ".mov", ".mkv", ".webm"]

    if input_path.is_file():
        return [input_path]

    if input_path.is_dir():
        videos = []
        for ext in extensions:
            videos.extend(input_path.glob(f"*{ext}"))
            videos.extend(input_path.glob(f"*{ext.upper()}"))
        return sorted(videos)

    logger.error(f"Input path does not exist: {input_path}")
    return []


def caption_video(
    video_path: Path,
    model_manager,
    max_length: int = 50,
    save_frames: bool = False,
    frames_dir: Path = None
) -> Optional[str]:
    """
    Generate caption for a single video.

    Args:
        video_path: Path to the video file
        model_manager: Initialized ModelManager
        max_length: Maximum caption length
        save_frames: Whether to save sampled frames
        frames_dir: Directory to save frames

    Returns:
        Generated caption or None if failed
    """
    try:
        logger.info(f"Processing: {video_path}")
        start_time = time.time()

        # Read video frames
        frames = read_video_frames(str(video_path))
        logger.debug(f"Read {len(frames)} frames")

        # Sample frames
        sampled = sample_frames(frames, HP.CLIP_LENGTH)
        logger.debug(f"Sampled {len(sampled)} frames")

        # Save frames if requested
        if save_frames and frames_dir:
            frames_dir.mkdir(parents=True, exist_ok=True)
            import cv2
            video_name = video_path.stem
            for i, frame in enumerate(sampled):
                frame_path = frames_dir / f"{video_name}_frame_{i}.jpg"
                # Convert RGB to BGR for OpenCV
                cv2.imwrite(str(frame_path), frame[:, :, ::-1])
            logger.info(f"Saved {len(sampled)} frames to {frames_dir}")

        # Convert to AV format
        converted = convert_frames_to_av(sampled)

        # Preprocess for model
        pixel_values = model_manager.preprocess_frames(converted)

        # Generate caption
        caption = model_manager.generate_caption(pixel_values, max_length)

        duration = time.time() - start_time
        logger.info(f"Caption ({duration:.2f}s): {caption}")

        return caption

    except Exception as e:
        logger.error(f"Failed to caption {video_path}: {e}", exc_info=True)
        return None


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Set up logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level=log_level, console_output=True)

    logger.info("=" * 60)
    logger.info("Batch Video Captioning")
    logger.info("=" * 60)

    # Get video files
    videos = get_video_files(args.input)
    if not videos:
        logger.error("No video files found")
        return 1

    logger.info(f"Found {len(videos)} video(s) to process")

    # Initialize model
    logger.info("Initializing ML models...")
    try:
        model_manager = get_model_manager()
        model_manager.initialize(args.model_dir)

        # Switch model if requested
        if args.model == "pulchowk":
            model_manager.switch_model(ModelType.PULCHOWK)

        logger.info(f"Using model: {model_manager.current_model_type.value}")
    except Exception as e:
        logger.critical(f"Failed to initialize models: {e}")
        return 1

    # Process videos
    results = []
    for video_path in videos:
        caption = caption_video(
            video_path,
            model_manager,
            max_length=args.max_length,
            save_frames=args.save_frames,
            frames_dir=args.frames_dir
        )
        if caption:
            results.append((video_path.name, caption))

    # Save results
    if results:
        output_file = args.output or "captions.csv"
        output_path = Path(output_file)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["video", "caption"])
            writer.writerows(results)

        logger.info(f"Saved {len(results)} captions to {output_path}")

    # Summary
    logger.info("=" * 60)
    logger.info(f"Processed: {len(videos)} videos")
    logger.info(f"Successful: {len(results)} captions")
    logger.info(f"Failed: {len(videos) - len(results)}")
    logger.info("=" * 60)

    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
