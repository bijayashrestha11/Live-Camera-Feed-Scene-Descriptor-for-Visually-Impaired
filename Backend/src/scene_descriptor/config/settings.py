"""
Application settings with environment variable support.

Uses Pydantic v2 BaseSettings for automatic .env file loading and validation.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", validation_alias="HOST")
    port: int = Field(default=8080, validation_alias="PORT")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # SSL Configuration
    ssl_cert_file: Optional[Path] = Field(default=None, validation_alias="SSL_CERT_FILE")
    ssl_key_file: Optional[Path] = Field(default=None, validation_alias="SSL_KEY_FILE")

    # Model Configuration
    model_dir: Path = Field(default=Path("ml-models"), validation_alias="MODEL_DIR")
    default_model: str = Field(default="git", validation_alias="DEFAULT_MODEL")
    cuda_device: str = Field(default="cuda:0", validation_alias="CUDA_DEVICE")

    # Processing Configuration
    frame_capture_seconds: int = Field(default=5, validation_alias="FRAME_CAPTURE_SECONDS")
    max_caption_length: int = Field(default=20, validation_alias="MAX_CAPTION_LENGTH")
    num_sample_frames: int = Field(default=6, validation_alias="NUM_SAMPLE_FRAMES")

    # Paths
    log_dir: Path = Field(default=Path("logs"), validation_alias="LOG_DIR")
    data_dir: Path = Field(default=Path("data"), validation_alias="DATA_DIR")

    @property
    def git_model_path(self) -> Path:
        """Path to the GIT model directory."""
        return self.model_dir / "git-base-vatex"

    @property
    def pulchowk_model_path(self) -> Path:
        """Path to the Pulchowk fine-tuned model directory."""
        return self.model_dir / "pulchowk-model"


# Global settings instance
settings = Settings()
