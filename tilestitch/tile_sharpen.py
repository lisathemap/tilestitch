"""Sharpening filter for stitched tile images."""

from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image, ImageFilter


class SharpenError(ValueError):
    pass


@dataclass
class SharpenConfig:
    enabled: bool = False
    factor: float = 1.0  # 0.0 = blurred, 1.0 = original, >1.0 = sharpened

    def __post_init__(self) -> None:
        if self.factor <= 0:
            raise SharpenError(f"factor must be positive, got {self.factor}")


def sharpen_config_from_env() -> SharpenConfig:
    enabled = os.environ.get("TILESTITCH_SHARPEN_ENABLED", "false").lower() == "true"
    factor = float(os.environ.get("TILESTITCH_SHARPEN_FACTOR", "2.0"))
    return SharpenConfig(enabled=enabled, factor=factor)


def apply_sharpen(image: Image.Image, config: SharpenConfig) -> Image.Image:
    """Apply an unsharp-mask-based sharpening to *image*.

    A *factor* of 1.0 returns the image unchanged.  Values above 1.0
    progressively sharpen; values between 0 and 1 soften.
    """
    if not config.enabled or config.factor == 1.0:
        return image

    blurred = image.filter(ImageFilter.GaussianBlur(radius=1))
    sharpened = Image.blend(blurred, image, config.factor)
    return sharpened
