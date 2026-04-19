"""Solarize effect: invert pixel values above a threshold."""
from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image, ImageOps


class SolarizeError(ValueError):
    """Raised when solarize configuration is invalid."""


@dataclass
class SolarizeConfig:
    enabled: bool = True
    threshold: int = 128

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise SolarizeError("enabled must be a bool")
        if not (0 <= self.threshold <= 255):
            raise SolarizeError("threshold must be between 0 and 255 inclusive")


def solarize_config_from_env() -> SolarizeConfig:
    """Build a SolarizeConfig from environment variables."""
    raw_enabled = os.environ.get("TILESTITCH_SOLARIZE_ENABLED", "false").strip().lower()
    enabled = raw_enabled in ("1", "true", "yes")
    threshold = int(os.environ.get("TILESTITCH_SOLARIZE_THRESHOLD", "128"))
    return SolarizeConfig(enabled=enabled, threshold=threshold)


def apply_solarize(image: Image.Image, config: SolarizeConfig) -> Image.Image:
    """Apply solarize effect to *image* using *config*."""
    if not config.enabled:
        return image
    rgb = image.convert("RGB")
    solarized = ImageOps.solarize(rgb, threshold=config.threshold)
    if image.mode == "RGBA":
        solarized = solarized.convert("RGBA")
        solarized.putalpha(image.getchannel("A"))
    return solarized
