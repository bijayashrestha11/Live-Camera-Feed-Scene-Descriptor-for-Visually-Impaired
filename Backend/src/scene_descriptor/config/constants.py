"""
Application constants and hyperparameters.

These are fixed values that don't change between environments.
For configurable values, see settings.py.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class HyperParameters:
    """Model and processing hyperparameters."""

    # Legacy constants (from original config.py)
    LATENT_DIM: int = 512
    NUM_ENCODER_TOKENS: int = 4096
    NUM_DECODER_TOKENS: int = 1500
    TIME_STEPS_ENCODER: int = 80
    MAX_PROBABILITY: int = -1
    MAX_LENGTH: int = 10

    # Frame processing
    NO_OF_SECONDS: int = 5  # Duration to collect frames before processing
    CLIP_LENGTH: int = 6  # Number of frames to sample for model
    FRAME_SAMPLE_RATE: int = 4

    # Model generation
    MAX_CAPTION_LENGTH: int = 20
    RANDOM_SEED: int = 40


@dataclass(frozen=True)
class ModelConstants:
    """ML model related constants."""

    GIT_MODEL_NAME: str = "microsoft/git-base-vatex"
    PULCHOWK_MODEL_FILE: str = "pulchowk-model.pkl"
    PROCESSOR_SUBDIR: str = "processor"
    MODEL_SUBDIR: str = "model"


@dataclass(frozen=True)
class WebRTCConstants:
    """WebRTC related constants."""

    DATA_CHANNEL_NAME: str = "chat"
    AUDIO_FILE: str = "demo-instruct.wav"


# Singleton instances
HP = HyperParameters()
MODEL_CONST = ModelConstants()
WEBRTC_CONST = WebRTCConstants()
