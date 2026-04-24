"""Spotlight effect: brightens a circular region and dims the surroundings."""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import Tuple

from PIL import Image
import numpy as np


class SpotlightError(ValueError):
    """Raised when spotlight configuration is invalid."""


@dataclass
class SpotlightConfig:
    cx: float = 0.5          # relative centre x  (0.0 – 1.0)
    cy: float = 0.5          # relative centre y  (0.0 – 1.0)
    radius: float = 0.4      # relative radius    (0.0 – 1.0)
    strength: float = 0.7    # dim factor outside (0.0 – 1.0)
    enabled: bool = True

    def __post_init__(self) -> None:
        for name, val in [("cx", self.cx), ("cy", self.cy), ("radius", self.radius)]:
            if not (0.0 <= val <= 1.0):
                raise SpotlightError(f"{name} must be between 0.0 and 1.0, got {val}")
        if not (0.0 <= self.strength <= 1.0):
            raise SpotlightError(
                f"strength must be between 0.0 and 1.0, got {self.strength}"
            )


def spotlight_config_from_env() -> SpotlightConfig:
    """Build a SpotlightConfig from environment variables."""
    def _f(key: str, default: float) -> float:
        return float(os.environ.get(key, default))

    def _b(key: str, default: bool) -> bool:
        raw = os.environ.get(key, str(default)).strip().lower()
        return raw in ("1", "true", "yes")

    return SpotlightConfig(
        cx=_f("TILESTITCH_SPOTLIGHT_CX", 0.5),
        cy=_f("TILESTITCH_SPOTLIGHT_CY", 0.5),
        radius=_f("TILESTITCH_SPOTLIGHT_RADIUS", 0.4),
        strength=_f("TILESTITCH_SPOTLIGHT_STRENGTH", 0.7),
        enabled=_b("TILESTITCH_SPOTLIGHT_ENABLED", True),
    )


def apply_spotlight(image: Image.Image, config: SpotlightConfig) -> Image.Image:
    """Apply a radial spotlight effect to *image*."""
    img = image.convert("RGBA")
    w, h = img.size

    cx_px = config.cx * w
    cy_px = config.cy * h
    radius_px = config.radius * min(w, h)

    xs = np.arange(w, dtype=np.float32)
    ys = np.arange(h, dtype=np.float32)
    xv, yv = np.meshgrid(xs, ys)

    dist = np.sqrt((xv - cx_px) ** 2 + (yv - cy_px) ** 2)
    mask = np.clip(1.0 - (dist - radius_px) / max(radius_px, 1.0), config.strength, 1.0)
    mask = (mask * 255).astype(np.uint8)

    r, g, b, a = img.split()
    mask_img = Image.fromarray(mask, mode="L")
    r = Image.fromarray(np.multiply(np.array(r) / 255.0, mask / 255.0) * 255).convert("L")
    g = Image.fromarray(np.multiply(np.array(g) / 255.0, mask / 255.0) * 255).convert("L")
    b = Image.fromarray(np.multiply(np.array(b) / 255.0, mask / 255.0) * 255).convert("L")

    result = Image.merge("RGBA", (r, g, b, a))
    return result if image.mode == "RGBA" else result.convert(image.mode)
