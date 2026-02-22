"""
ML Model Manager for Scene Descriptor.

Handles loading, switching, and inference with ML models.
Uses singleton pattern to ensure only one instance exists.
"""

import copy
import time
from pathlib import Path
from typing import Optional

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoProcessor

from ..config import settings, MODEL_CONST, HP
from ..enums import ModelType, ModelStatus
from ..utils.logging import get_logger
from ..utils.exceptions import (
    ModelLoadError,
    ModelInferenceError,
    ModelNotFoundError,
    ModelNotInitializedError,
)

logger = get_logger(__name__)


class ModelManager:
    """
    Singleton class for managing ML models.

    Handles:
    - Loading models from HuggingFace or local storage
    - Switching between different models (GIT, Pulchowk)
    - Running inference for caption generation
    """

    _instance: Optional["ModelManager"] = None

    def __new__(cls) -> "ModelManager":
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize model manager (only runs once due to singleton)."""
        if self._initialized:
            return

        self._processor: Optional[AutoProcessor] = None
        self._current_model: Optional[AutoModelForCausalLM] = None
        self._git_model: Optional[AutoModelForCausalLM] = None
        self._pulchowk_model: Optional[AutoModelForCausalLM] = None
        self._device: Optional[torch.device] = None
        self._current_model_type: ModelType = ModelType.GIT
        self._status: ModelStatus = ModelStatus.NOT_LOADED

        self._initialized = True
        logger.info("ModelManager initialized")

    @classmethod
    def get_instance(cls) -> "ModelManager":
        """Get the singleton instance of ModelManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None

    @property
    def status(self) -> ModelStatus:
        """Get current model status."""
        return self._status

    @property
    def current_model_type(self) -> ModelType:
        """Get the type of currently active model."""
        return self._current_model_type

    @property
    def device(self) -> torch.device:
        """Get the device models are running on."""
        if self._device is None:
            raise ModelNotInitializedError("Models not initialized. Call initialize() first.")
        return self._device

    @property
    def processor(self) -> AutoProcessor:
        """Get the image processor."""
        if self._processor is None:
            raise ModelNotInitializedError("Models not initialized. Call initialize() first.")
        return self._processor

    @property
    def model(self) -> AutoModelForCausalLM:
        """Get the currently active model."""
        if self._current_model is None:
            raise ModelNotInitializedError("Models not initialized. Call initialize() first.")
        return self._current_model

    def initialize(self, model_dir: Optional[Path] = None) -> None:
        """
        Initialize and load ML models.

        Args:
            model_dir: Directory containing model files. Uses settings.model_dir if None.

        Raises:
            ModelLoadError: If models cannot be loaded
        """
        self._status = ModelStatus.LOADING
        model_dir = model_dir or settings.model_dir
        model_dir = Path(model_dir)

        try:
            # Set up device
            self._setup_device()

            # Load GIT model (required)
            self._load_git_model(model_dir)

            # Load Pulchowk model (optional)
            self._load_pulchowk_model(model_dir)

            # Set default model
            self._current_model = self._git_model
            self._current_model_type = ModelType.GIT

            # Set random seed for reproducibility
            np.random.seed(HP.RANDOM_SEED)

            self._status = ModelStatus.READY
            logger.info(f"ModelManager ready with {self._current_model_type.value} model on {self._device}")

        except Exception as e:
            self._status = ModelStatus.ERROR
            raise ModelLoadError(f"Failed to initialize models: {e}", cause=e)

    def _setup_device(self) -> None:
        """Set up the compute device (CUDA or CPU)."""
        if torch.cuda.is_available():
            self._device = torch.device(settings.cuda_device)
            logger.info(f"Using CUDA device: {settings.cuda_device}")
        else:
            self._device = torch.device("cpu")
            logger.warning("CUDA not available, using CPU")

    def _load_git_model(self, model_dir: Path) -> None:
        """Load the GIT-base-vatex model."""
        git_path = model_dir / "git-base-vatex"

        if not git_path.exists():
            logger.info("GIT model not found locally, downloading from HuggingFace...")
            try:
                self._processor = AutoProcessor.from_pretrained(MODEL_CONST.GIT_MODEL_NAME)
                self._git_model = AutoModelForCausalLM.from_pretrained(MODEL_CONST.GIT_MODEL_NAME)

                # Save locally for future use
                git_path.mkdir(parents=True, exist_ok=True)
                self._processor.save_pretrained(git_path / MODEL_CONST.PROCESSOR_SUBDIR)
                self._git_model.save_pretrained(git_path / MODEL_CONST.MODEL_SUBDIR)

                logger.info("GIT model downloaded and saved locally")
            except Exception as e:
                raise ModelLoadError(f"Failed to download GIT model: {e}", cause=e)
        else:
            logger.info("Loading GIT model from local storage...")
            try:
                self._processor = AutoProcessor.from_pretrained(
                    git_path / MODEL_CONST.PROCESSOR_SUBDIR
                )
                self._git_model = AutoModelForCausalLM.from_pretrained(
                    git_path / MODEL_CONST.MODEL_SUBDIR
                )
                logger.info("GIT model loaded successfully")
            except Exception as e:
                raise ModelLoadError(f"Failed to load GIT model: {e}", cause=e)

        # Move model to device
        self._git_model.to(self._device)

    def _load_pulchowk_model(self, model_dir: Path) -> None:
        """Load the Pulchowk fine-tuned model if available."""
        pulchowk_path = model_dir / "pulchowk-model"
        model_file = pulchowk_path / MODEL_CONST.PULCHOWK_MODEL_FILE

        if pulchowk_path.exists() and model_file.exists():
            logger.info("Loading Pulchowk model...")
            try:
                # Create a copy of the GIT model architecture
                self._pulchowk_model = copy.deepcopy(self._git_model)

                # Load the fine-tuned weights
                self._pulchowk_model.load_state_dict(
                    torch.load(model_file, map_location=self._device),
                    strict=True
                )

                logger.info("Pulchowk model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load Pulchowk model: {e}")
                self._pulchowk_model = None
        else:
            logger.info("Pulchowk model not found, skipping")
            self._pulchowk_model = None

    def switch_model(self, model_type: ModelType) -> str:
        """
        Switch to a different model.

        Args:
            model_type: The model type to switch to

        Returns:
            Name of the activated model

        Raises:
            ModelNotFoundError: If requested model is not available
        """
        if model_type == ModelType.PULCHOWK:
            if self._pulchowk_model is None:
                raise ModelNotFoundError("Pulchowk model is not available")
            self._current_model = self._pulchowk_model
            self._current_model_type = ModelType.PULCHOWK
            logger.info("Switched to Pulchowk model")
        elif model_type == ModelType.GIT:
            if self._git_model is None:
                raise ModelNotFoundError("GIT model is not available")
            self._current_model = self._git_model
            self._current_model_type = ModelType.GIT
            logger.info("Switched to GIT model")
        else:
            raise ModelNotFoundError(f"Unknown model type: {model_type}")

        return self._current_model_type.value

    def generate_caption(
        self,
        pixel_values: torch.Tensor,
        max_length: Optional[int] = None
    ) -> str:
        """
        Generate a caption from processed frames.

        Args:
            pixel_values: Preprocessed frames tensor
            max_length: Maximum caption length (uses settings default if None)

        Returns:
            Generated caption string

        Raises:
            ModelInferenceError: If caption generation fails
        """
        if self._current_model is None:
            raise ModelNotInitializedError("Model not initialized")

        self._status = ModelStatus.PROCESSING
        max_length = max_length or settings.max_caption_length

        try:
            start_time = time.time()
            logger.debug(f"Generating caption with max_length={max_length}")

            with torch.no_grad():
                generated_ids = self._current_model.generate(
                    pixel_values=pixel_values,
                    max_length=max_length
                )

            caption = self._processor.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]

            duration = time.time() - start_time
            logger.info(f"Caption generated in {duration:.2f}s: {caption[:50]}...")

            self._status = ModelStatus.READY
            return caption

        except Exception as e:
            self._status = ModelStatus.ERROR
            raise ModelInferenceError(f"Caption generation failed: {e}", cause=e)

    def preprocess_frames(self, frames: np.ndarray) -> torch.Tensor:
        """
        Preprocess frames for model input.

        Args:
            frames: Array of video frames (N, H, W, C)

        Returns:
            Preprocessed tensor ready for model input
        """
        if self._processor is None:
            raise ModelNotInitializedError("Processor not initialized")

        pixel_values = self._processor(
            images=list(frames),
            return_tensors="pt"
        ).pixel_values

        return pixel_values.to(self._device)

    def is_ready(self) -> bool:
        """Check if the model manager is ready for inference."""
        return self._status == ModelStatus.READY

    def has_pulchowk_model(self) -> bool:
        """Check if Pulchowk model is available."""
        return self._pulchowk_model is not None


# Convenience function for getting the singleton instance
def get_model_manager() -> ModelManager:
    """Get the ModelManager singleton instance."""
    return ModelManager.get_instance()
