"""Tile relief shadow: cast a directional drop-shadow on map tiles."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Tuple

from PIL import Image, ImageFilter


class ReliefShadowError(ValueError):
    """Raised when ReliefShadowConfig receives invalid parameters."""


@dataclass
class ReliefShadowConfig:
    enabled: bool = True
    angle: float = 315.0       # degrees, 0 = right, 90 = down
    distance: int = 4          # pixels
    blur_radius: float = 2.0
    opacity: float = 0.5       # 0.0 – 1.0
    colour: Tuple[int, int, int] = field(default_factory=lambda: (0, 0, 0))

    def __post_init__(self) -> None:
        if not (0.0 <= self.opacity <= 1.0):
            raise ReliefShadowError(f"opacity must be in [0, 1], got {self.opacity}")
        if self.distance < 0:
            raise ReliefShadowError(f"distance must be >= 0, got {self.distance}")
        if self.blur_radius < 0:
            raise ReliefShadowError(f"blur_radius must be >= 0, got {self.blur_radius}")


def relief_shadow_config_from_env() -> ReliefShadowConfig:
    """Build a ReliefShadowConfig from environment variables."""
    import os

    def _float(key: str, default: float) -> float:
        return float(os.environ.get(key, default))

    def _int(key: str, default: int) -> int:
        return int(os.environ.get(key, default))

    def _bool(key: str, default: bool) -> bool:
        val = os.environ.get(key)
        if val is None:
            return default
        return val.strip().lower() in ("1", "true", "yes")

    return ReliefShadowConfig(
        enabled=_bool("TILESTITCH_SHADOW_ENABLED", True),
        angle=_float("TILESTITCH_SHADOW_ANGLE", 315.0),
        distance=_int("TILESTITCH_SHADOW_DISTANCE", 4),
        blur_radius=_float("TILESTITCH_SHADOW_BLUR", 2.0),
        opacity=_float("TILESTITCH_SHADOW_OPACITY", 0.5),
    )


def apply_relief_shadow(image: Image.Image, config: ReliefShadowConfig) -> Image.Image:
    """Apply a directional drop-shadow to *image* and return the result."""
    if not config.enabled:
        return image

    src = image.convert("RGBA")
    w, h = src.size

    # Compute offset from angle + distance
    rad = math.radians(config.angle)
    dx = int(round(config.distance * math.cos(rad)))
    dy = int(round(config.distance * math.sin(rad)))

    # Build shadow layer from alpha channel
    alpha = src.getchannel("A")
    shadow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    r, g, b = config.colour
    shadow_colour = Image.new("RGBA", (w, h), (r, g, b, 255))
    shadow_layer.paste(shadow_colour, mask=alpha)

    if config.blur_radius > 0:
        shadow_layer = shadow_layer.filter(
            ImageFilter.GaussianBlur(radius=config.blur_radius)
        )

    # Shift the shadow
    shifted = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shifted.paste(shadow_layer, (dx, dy))

    # Blend shadow with original
    alpha_val = int(config.opacity * 255)
    shifted_data = shifted.split()
    blended_alpha = shifted_data[3].point(lambda p: int(p * config.opacity))
    shifted = Image.merge("RGBA", (*shifted_data[:3], blended_alpha))

    composite = Image.alpha_composite(shifted, src)
    return composite
