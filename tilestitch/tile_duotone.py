"""Duotone effect: map image luminance to a two-colour gradient."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple

from PIL import Image
import numpy as np

Colour = Tuple[int, int, int]


class DuotoneError(ValueError):
    """Raised when duotone configuration is invalid."""


def _parse_colour(value: str) -> Colour:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise DuotoneError(f"Colour must be a 6-digit hex string, got: {value!r}")
    try:
        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)
    except ValueError:
        raise DuotoneError(f"Invalid hex colour: {value!r}")
    return (r, g, b)


@dataclass
class DuotoneConfig:
    """Configuration for the duotone effect."""

    shadow: str = "000000"
    highlight: str = "ffffff"
    enabled: bool = True

    def __post_init__(self) -> None:
        _parse_colour(self.shadow)
        _parse_colour(self.highlight)

    @property
    def shadow_rgb(self) -> Colour:
        return _parse_colour(self.shadow)

    @property
    def highlight_rgb(self) -> Colour:
        return _parse_colour(self.highlight)


def duotone_config_from_env() -> DuotoneConfig:
    shadow = os.environ.get("TILESTITCH_DUOTONE_SHADOW", "000000")
    highlight = os.environ.get("TILESTITCH_DUOTONE_HIGHLIGHT", "ffffff")
    enabled = os.environ.get("TILESTITCH_DUOTONE_ENABLED", "true").strip().lower() == "true"
    return DuotoneConfig(shadow=shadow, highlight=highlight, enabled=enabled)


def apply_duotone(image: Image.Image, config: DuotoneConfig) -> Image.Image:
    """Apply a duotone effect to *image* using the shadow and highlight colours."""
    grey = image.convert("L")
    arr = np.array(grey, dtype=np.float32) / 255.0  # 0.0 – 1.0

    sr, sg, sb = config.shadow_rgb
    hr, hg, hb = config.highlight_rgb

    r = (sr + (hr - sr) * arr).astype(np.uint8)
    g = (sg + (hg - sg) * arr).astype(np.uint8)
    b = (sb + (hb - sb) * arr).astype(np.uint8)

    rgb = np.stack([r, g, b], axis=-1)
    result = Image.fromarray(rgb, mode="RGB")

    if image.mode == "RGBA":
        result = result.convert("RGBA")
        result.putalpha(image.getchannel("A"))

    return result
