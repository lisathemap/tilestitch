"""Colour temperature adjustment for stitched map tiles."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image


class TemperatureError(Exception):
    """Raised when temperature configuration is invalid."""


def temperature_config_from_env() -> "TemperatureConfig":
    import os

    enabled = os.environ.get("TILESTITCH_TEMPERATURE_ENABLED", "false").strip().lower() == "true"
    shift = float(os.environ.get("TILESTITCH_TEMPERATURE_SHIFT", "0"))
    return TemperatureConfig(enabled=enabled, shift=shift)


@dataclass
class TemperatureConfig:
    """Configuration for colour temperature adjustment.

    shift > 0 warms the image (boosts red, reduces blue).
    shift < 0 cools the image (boosts blue, reduces red).
    Acceptable range: -1.0 to 1.0.
    """

    enabled: bool = False
    shift: float = 0.0

    def __post_init__(self) -> None:
        if not -1.0 <= self.shift <= 1.0:
            raise TemperatureError(
                f"shift must be between -1.0 and 1.0, got {self.shift}"
            )


def apply_temperature(image: Image.Image, config: TemperatureConfig) -> Image.Image:
    """Adjust the colour temperature of *image* according to *config*."""
    if not config.enabled or config.shift == 0.0:
        return image

    rgba = image.convert("RGBA")
    r, g, b, a = rgba.split()

    strength = int(abs(config.shift) * 40)

    if config.shift > 0:
        # Warm: increase red, decrease blue
        r = r.point(lambda v: min(255, v + strength))
        b = b.point(lambda v: max(0, v - strength))
    else:
        # Cool: increase blue, decrease red
        b = b.point(lambda v: min(255, v + strength))
        r = r.point(lambda v: max(0, v - strength))

    result = Image.merge("RGBA", (r, g, b, a))
    return result if image.mode == "RGBA" else result.convert(image.mode)
