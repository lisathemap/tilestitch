"""Vignette effect for stitched map images."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from PIL import Image, ImageFilter
import numpy as np


class VignetteError(Exception):
    """Raised when vignette configuration is invalid."""


@dataclass
class VignetteConfig:
    enabled: bool = True
    strength: float = 0.5  # 0.0 – 1.0
    radius: float = 1.0    # relative radius (1.0 = fits image)

    def __post_init__(self) -> None:
        if not 0.0 < self.strength <= 1.0:
            raise VignetteError(f"strength must be in (0, 1], got {self.strength}")
        if self.radius <= 0.0:
            raise VignetteError(f"radius must be positive, got {self.radius}")


def vignette_config_from_env() -> VignetteConfig:
    import os
    enabled = os.getenv("TILESTITCH_VIGNETTE_ENABLED", "false").lower() == "true"
    strength = float(os.getenv("TILESTITCH_VIGNETTE_STRENGTH", "0.5"))
    radius = float(os.getenv("TILESTITCH_VIGNETTE_RADIUS", "1.0"))
    return VignetteConfig(enabled=enabled, strength=strength, radius=radius)


def apply_vignette(image: Image.Image, config: VignetteConfig) -> Image.Image:
    """Overlay a radial vignette on *image* and return a new RGBA image."""
    img = image.convert("RGBA")
    w, h = img.size
    cx, cy = w / 2.0, h / 2.0
    max_dist = math.sqrt(cx ** 2 + cy ** 2) * config.radius

    xs = np.linspace(0, w - 1, w)
    ys = np.linspace(0, h - 1, h)
    xv, yv = np.meshgrid(xs, ys)
    dist = np.sqrt((xv - cx) ** 2 + (yv - cy) ** 2)
    mask = np.clip(dist / max_dist, 0.0, 1.0) * config.strength
    alpha = (mask * 255).astype(np.uint8)

    overlay = Image.fromarray(alpha, mode="L").convert("RGBA")
    overlay_arr = np.array(overlay)
    overlay_arr[:, :, :3] = 0  # black vignette
    overlay_arr[:, :, 3] = alpha
    vignette_layer = Image.fromarray(overlay_arr, mode="RGBA")

    result = Image.alpha_composite(img, vignette_layer)
    return result
