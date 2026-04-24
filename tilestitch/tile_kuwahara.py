"""Kuwahara filter for painterly / oil-painting effect on tiles."""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
from PIL import Image


class KuwaharaError(Exception):
    """Raised when Kuwahara filter configuration or application fails."""


@dataclass
class KuwaharaConfig:
    enabled: bool = True
    radius: int = 3

    def __post_init__(self) -> None:
        if self.radius < 1:
            raise KuwaharaError(f"radius must be >= 1, got {self.radius}")
        if self.radius > 10:
            raise KuwaharaError(f"radius must be <= 10, got {self.radius}")


def kuwahara_config_from_env() -> KuwaharaConfig:
    """Build a KuwaharaConfig from environment variables."""
    enabled = os.environ.get("TILESTITCH_KUWAHARA_ENABLED", "true").strip().lower() != "false"
    radius = int(os.environ.get("TILESTITCH_KUWAHARA_RADIUS", "3"))
    return KuwaharaConfig(enabled=enabled, radius=radius)


def apply_kuwahara(image: Image.Image, config: KuwaharaConfig) -> Image.Image:
    """Apply a Kuwahara (painterly) filter to *image*."""
    if not config.enabled:
        return image

    src = image.convert("RGB")
    arr = np.array(src, dtype=np.float32)
    out = np.empty_like(arr)
    r = config.radius

    h, w = arr.shape[:2]
    padded = np.pad(arr, ((r, r), (r, r), (0, 0)), mode="edge")

    # Four quadrant offsets: top-left, top-right, bottom-left, bottom-right
    offsets = [
        (0, r + 1, 0, r + 1),
        (0, r + 1, r, 2 * r + 1),
        (r, 2 * r + 1, 0, r + 1),
        (r, 2 * r + 1, r, 2 * r + 1),
    ]

    for y in range(h):
        for x in range(w):
            best_var = float("inf")
            best_mean = arr[y, x]
            for (ry0, ry1, rx0, rx1) in offsets:
                region = padded[y + ry0 : y + ry1, x + rx0 : x + rx1]
                mean = region.mean(axis=(0, 1))
                var = region.var(axis=(0, 1)).sum()
                if var < best_var:
                    best_var = var
                    best_mean = mean
            out[y, x] = best_mean

    result = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
    if image.mode == "RGBA":
        result = result.convert("RGBA")
        result.putalpha(image.split()[3])
    return result
