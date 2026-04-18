"""Threshold (posterise) filter for stitched tile images."""
from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image, ImageOps


class ThresholdError(ValueError):
    """Raised when threshold configuration is invalid."""


@dataclass
class ThresholdConfig:
    """Configuration for the threshold filter."""

    enabled: bool = False
    level: int = 128  # 0-255

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise ThresholdError("enabled must be a bool")
        if not (0 <= self.level <= 255):
            raise ThresholdError(f"level must be 0-255, got {self.level}")


def threshold_config_from_env() -> ThresholdConfig:
    """Build a ThresholdConfig from environment variables.

    TILESTITCH_THRESHOLD_ENABLED  - '1' or 'true' to enable
    TILESTITCH_THRESHOLD_LEVEL    - integer 0-255 (default 128)
    """
    enabled = os.getenv("TILESTITCH_THRESHOLD_ENABLED", "0").lower() in ("1", "true")
    level = int(os.getenv("TILESTITCH_THRESHOLD_LEVEL", "128"))
    return ThresholdConfig(enabled=enabled, level=level)


def apply_threshold(image: Image.Image, config: ThresholdConfig) -> Image.Image:
    """Convert *image* to black-and-white using *config.level* as the cutoff.

    The image is first converted to grayscale, thresholded, then converted
    back to RGBA so it is compatible with the rest of the pipeline.
    """
    if not config.enabled:
        return image

    grey = image.convert("L")
    bw = grey.point(lambda p: 255 if p >= config.level else 0, "1")
    return bw.convert("RGBA")
