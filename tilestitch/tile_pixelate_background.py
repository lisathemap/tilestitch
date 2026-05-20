"""Pixelate background regions outside a masked area."""
from __future__ import annotations

import os
from dataclasses import dataclass
from PIL import Image, ImageFilter


class PixelateBackgroundError(Exception):
    """Raised when background pixelation configuration is invalid."""


@dataclass
class PixelateBackgroundConfig:
    enabled: bool = True
    block_size: int = 16
    mask_cx: float = 0.5
    mask_cy: float = 0.5
    mask_radius: float = 0.3

    def __post_init__(self) -> None:
        if self.block_size < 1:
            raise PixelateBackgroundError("block_size must be >= 1")
        if not (0.0 <= self.mask_cx <= 1.0):
            raise PixelateBackgroundError("mask_cx must be between 0.0 and 1.0")
        if not (0.0 <= self.mask_cy <= 1.0):
            raise PixelateBackgroundError("mask_cy must be between 0.0 and 1.0")
        if self.mask_radius <= 0.0:
            raise PixelateBackgroundError("mask_radius must be > 0.0")
        if self.mask_radius > 1.0:
            raise PixelateBackgroundError("mask_radius must be <= 1.0")


def pixelate_background_config_from_env() -> PixelateBackgroundConfig:
    return PixelateBackgroundConfig(
        enabled=os.environ.get("PIXELATE_BG_ENABLED", "true").strip().lower() == "true",
        block_size=int(os.environ.get("PIXELATE_BG_BLOCK_SIZE", "16")),
        mask_cx=float(os.environ.get("PIXELATE_BG_MASK_CX", "0.5")),
        mask_cy=float(os.environ.get("PIXELATE_BG_MASK_CY", "0.5")),
        mask_radius=float(os.environ.get("PIXELATE_BG_MASK_RADIUS", "0.3")),
    )


def apply_pixelate_background(image: Image.Image, config: PixelateBackgroundConfig) -> Image.Image:
    """Pixelate everything outside a circular mask region."""
    if not config.enabled:
        return image

    w, h = image.size
    bs = config.block_size

    small = image.resize((max(1, w // bs), max(1, h // bs)), Image.NEAREST)
    pixelated = small.resize((w, h), Image.NEAREST)

    mask = Image.new("L", (w, h), 0)
    import math
    cx = int(config.mask_cx * w)
    cy = int(config.mask_cy * h)
    radius = int(config.mask_radius * min(w, h))

    pixels = mask.load()
    for y in range(h):
        for x in range(w):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist <= radius:
                pixels[x, y] = 255

    result = image.copy().convert("RGBA")
    pixelated_rgba = pixelated.convert("RGBA")
    result = Image.composite(result, pixelated_rgba, mask)
    return result.convert(image.mode) if image.mode != "RGBA" else result
