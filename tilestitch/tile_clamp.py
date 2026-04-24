"""Pixel value clamping — restrict channel values to a specified range."""

from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image


class ClampError(Exception):
    """Raised when clamping configuration is invalid."""


@dataclass
class ClampConfig:
    """Configuration for pixel value clamping."""

    enabled: bool = True
    low: int = 0
    high: int = 255

    def __post_init__(self) -> None:
        if self.low < 0 or self.low > 255:
            raise ClampError(f"low must be 0-255, got {self.low}")
        if self.high < 0 or self.high > 255:
            raise ClampError(f"high must be 0-255, got {self.high}")
        if self.low >= self.high:
            raise ClampError(
                f"low ({self.low}) must be strictly less than high ({self.high})"
            )


def clamp_config_from_env() -> ClampConfig:
    """Build a :class:`ClampConfig` from environment variables.

    Variables
    ---------
    TILESTITCH_CLAMP_ENABLED : '1'/'0', default '1'
    TILESTITCH_CLAMP_LOW     : int 0-254, default 0
    TILESTITCH_CLAMP_HIGH    : int 1-255, default 255
    """
    enabled = os.environ.get("TILESTITCH_CLAMP_ENABLED", "1") == "1"
    low = int(os.environ.get("TILESTITCH_CLAMP_LOW", "0"))
    high = int(os.environ.get("TILESTITCH_CLAMP_HIGH", "255"))
    return ClampConfig(enabled=enabled, low=low, high=high)


def apply_clamp(image: Image.Image, config: ClampConfig) -> Image.Image:
    """Clamp each channel of *image* to [config.low, config.high].

    The image is converted to RGBA for processing and returned as RGBA.
    The alpha channel is left untouched.
    """
    if not config.enabled:
        return image

    rgba = image.convert("RGBA")
    r, g, b, a = rgba.split()

    def _clamp_band(band: Image.Image) -> Image.Image:
        lut = [
            max(config.low, min(config.high, v)) for v in range(256)
        ]
        return band.point(lut)

    clamped = Image.merge("RGBA", (_clamp_band(r), _clamp_band(g), _clamp_band(b), a))
    return clamped
