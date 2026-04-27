"""Barrel/pincushion lens distortion effect for tiles."""

from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image


class LensDistortionError(Exception):
    """Raised when lens distortion configuration is invalid."""


@dataclass
class LensDistortionConfig:
    """Configuration for lens distortion.

    k1: radial distortion coefficient (positive = barrel, negative = pincushion).
    k2: secondary radial distortion coefficient.
    enabled: whether the effect is active.
    """

    k1: float = 0.1
    k2: float = 0.0
    enabled: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise LensDistortionError("enabled must be a bool")
        if abs(self.k1) > 1.0:
            raise LensDistortionError("k1 must be in the range [-1.0, 1.0]")
        if abs(self.k2) > 1.0:
            raise LensDistortionError("k2 must be in the range [-1.0, 1.0]")


def lens_distortion_config_from_env() -> LensDistortionConfig:
    """Build a LensDistortionConfig from environment variables."""
    k1 = float(os.environ.get("TILESTITCH_LENS_K1", "0.1"))
    k2 = float(os.environ.get("TILESTITCH_LENS_K2", "0.0"))
    enabled = os.environ.get("TILESTITCH_LENS_ENABLED", "true").lower() == "true"
    return LensDistortionConfig(k1=k1, k2=k2, enabled=enabled)


def apply_lens_distortion(image: Image.Image, config: LensDistortionConfig) -> Image.Image:
    """Apply radial lens distortion to *image*.

    Uses a polynomial radial distortion model sampled per-pixel.
    """
    if not config.enabled:
        return image

    import numpy as np

    src = image.convert("RGBA")
    w, h = src.size
    cx, cy = w / 2.0, h / 2.0
    max_r = (cx ** 2 + cy ** 2) ** 0.5

    xs, ys = np.meshgrid(np.arange(w), np.arange(h))
    dx = (xs - cx) / max_r
    dy = (ys - cy) / max_r
    r2 = dx ** 2 + dy ** 2
    factor = 1.0 + config.k1 * r2 + config.k2 * r2 ** 2

    src_x = np.clip(cx + dx * factor * max_r, 0, w - 1).astype(np.float32)
    src_y = np.clip(cy + dy * factor * max_r, 0, h - 1).astype(np.float32)

    arr = np.array(src)
    xi = src_x.astype(int)
    yi = src_y.astype(int)
    out = arr[yi, xi]
    return Image.fromarray(out.astype(np.uint8), mode="RGBA")
