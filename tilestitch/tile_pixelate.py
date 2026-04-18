from __future__ import annotations

import os
from dataclasses import dataclass
from PIL import Image


class PixelateError(Exception):
    """Raised when pixelation cannot be applied."""


@dataclass
class PixelateConfig:
    block_size: int = 8
    enabled: bool = True

    def __post_init__(self) -> None:
        if self.block_size < 1:
            raise PixelateError("block_size must be at least 1")
        if self.block_size > 256:
            raise PixelateError("block_size must not exceed 256")


def pixelate_config_from_env() -> PixelateConfig:
    block_size = int(os.environ.get("TILESTITCH_PIXELATE_BLOCK_SIZE", "8"))
    enabled_raw = os.environ.get("TILESTITCH_PIXELATE_ENABLED", "true").lower()
    enabled = enabled_raw not in ("0", "false", "no")
    return PixelateConfig(block_size=block_size, enabled=enabled)


def apply_pixelate(image: Image.Image, config: PixelateConfig) -> Image.Image:
    """Pixelate an image by downscaling then upscaling."""
    if not config.enabled:
        return image
    orig_size = image.size
    small_w = max(1, orig_size[0] // config.block_size)
    small_h = max(1, orig_size[1] // config.block_size)
    small = image.resize((small_w, small_h), Image.NEAREST)
    return small.resize(orig_size, Image.NEAREST)
