"""Noise reduction filter for stitched tile images."""
from __future__ import annotations

from dataclasses import dataclass
from PIL import Image, ImageFilter


class NoiseError(ValueError):
    """Raised when noise reduction configuration is invalid."""


@dataclass
class NoiseConfig:
    enabled: bool = False
    radius: int = 1

    def __post_init__(self) -> None:
        if self.radius < 1:
            raise NoiseError(f"radius must be >= 1, got {self.radius}")
        if self.radius > 10:
            raise NoiseError(f"radius must be <= 10, got {self.radius}")


def noise_config_from_env() -> NoiseConfig:
    import os

    enabled = os.getenv("TILESTITCH_NOISE_ENABLED", "false").strip().lower() == "true"
    radius = int(os.getenv("TILESTITCH_NOISE_RADIUS", "1"))
    return NoiseConfig(enabled=enabled, radius=radius)


def apply_noise_reduction(image: Image.Image, config: NoiseConfig) -> Image.Image:
    """Apply a median filter to reduce noise in *image*."""
    if not config.enabled:
        return image
    mode = image.mode
    working = image.convert("RGB") if mode not in ("RGB", "L") else image
    filtered = working.filter(ImageFilter.MedianFilter(size=config.radius * 2 + 1))
    if mode != working.mode:
        filtered = filtered.convert(mode)
    return filtered
