"""Brightness and contrast adjustment for stitched tile images."""
from __future__ import annotations

import os
from dataclasses import dataclass
from PIL import Image, ImageEnhance


class BrightnessError(ValueError):
    pass


@dataclass
class BrightnessConfig:
    brightness: float = 1.0
    contrast: float = 1.0

    def __post_init__(self) -> None:
        if not (0.0 < self.brightness <= 4.0):
            raise BrightnessError(f"brightness must be in (0, 4], got {self.brightness}")
        if not (0.0 < self.contrast <= 4.0):
            raise BrightnessError(f"contrast must be in (0, 4], got {self.contrast}")


def brightness_config_from_env() -> BrightnessConfig:
    brightness = float(os.environ.get("TILESTITCH_BRIGHTNESS", "1.0"))
    contrast = float(os.environ.get("TILESTITCH_CONTRAST", "1.0"))
    return BrightnessConfig(brightness=brightness, contrast=contrast)


def adjust_brightness(image: Image.Image, config: BrightnessConfig) -> Image.Image:
    """Apply brightness and contrast adjustments to *image*."""
    img = image
    if config.brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(config.brightness)
    if config.contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(config.contrast)
    return img
