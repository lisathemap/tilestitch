"""Pixel sorting effect for map tiles."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from PIL import Image
import numpy as np


class PixelSortError(Exception):
    """Raised when pixel sort configuration or processing fails."""


_VALID_AXES = ("x", "y")
_VALID_KEYS = ("brightness", "hue", "saturation")


@dataclass
class PixelSortConfig:
    enabled: bool = True
    axis: Literal["x", "y"] = "x"
    sort_key: Literal["brightness", "hue", "saturation"] = "brightness"
    threshold_low: float = 0.2
    threshold_high: float = 0.8
    reverse: bool = False

    def __post_init__(self) -> None:
        if self.axis not in _VALID_AXES:
            raise PixelSortError(f"axis must be one of {_VALID_AXES}, got {self.axis!r}")
        if self.sort_key not in _VALID_KEYS:
            raise PixelSortError(f"sort_key must be one of {_VALID_KEYS}, got {self.sort_key!r}")
        if not (0.0 <= self.threshold_low <= 1.0):
            raise PixelSortError("threshold_low must be in [0.0, 1.0]")
        if not (0.0 <= self.threshold_high <= 1.0):
            raise PixelSortError("threshold_high must be in [0.0, 1.0]")
        if self.threshold_low >= self.threshold_high:
            raise PixelSortError("threshold_low must be less than threshold_high")


def _pixel_key(pixels: np.ndarray, key: str) -> np.ndarray:
    """Return a 1-D float array of sort keys for a row/column of RGBA pixels."""
    r = pixels[:, 0].astype(float) / 255.0
    g = pixels[:, 1].astype(float) / 255.0
    b = pixels[:, 2].astype(float) / 255.0
    if key == "brightness":
        return 0.299 * r + 0.587 * g + 0.114 * b
    if key == "saturation":
        cmax = np.maximum(np.maximum(r, g), b)
        cmin = np.minimum(np.minimum(r, g), b)
        return np.where(cmax == 0, 0.0, (cmax - cmin) / cmax)
    # hue
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin
    hue = np.zeros_like(r)
    mask = delta != 0
    idx_r = mask & (cmax == r)
    idx_g = mask & (cmax == g)
    idx_b = mask & (cmax == b)
    hue[idx_r] = ((g[idx_r] - b[idx_r]) / delta[idx_r]) % 6
    hue[idx_g] = (b[idx_g] - r[idx_g]) / delta[idx_g] + 2
    hue[idx_b] = (r[idx_b] - g[idx_b]) / delta[idx_b] + 4
    return hue / 6.0


def apply_pixelsort(image: Image.Image, config: PixelSortConfig) -> Image.Image:
    """Apply pixel sorting along the configured axis."""
    img = image.convert("RGBA")
    arr = np.array(img)
    h, w = arr.shape[:2]
    lines = range(h) if config.axis == "x" else range(w)
    for i in lines:
        row = arr[i, :, :] if config.axis == "x" else arr[:, i, :]
        keys = _pixel_key(row, config.sort_key)
        mask = (keys >= config.threshold_low) & (keys <= config.threshold_high)
        indices = np.where(mask)[0]
        if indices.size < 2:
            continue
        segment = row[indices]
        seg_keys = keys[indices]
        order = np.argsort(seg_keys)
        if config.reverse:
            order = order[::-1]
        sorted_segment = segment[order]
        if config.axis == "x":
            arr[i, indices, :] = sorted_segment
        else:
            arr[indices, i, :] = sorted_segment
    return Image.fromarray(arr, "RGBA")


def pixelsort_config_from_env() -> PixelSortConfig:
    import os
    return PixelSortConfig(
        enabled=os.environ.get("TILESTITCH_PIXELSORT_ENABLED", "true").lower() == "true",
        axis=os.environ.get("TILESTITCH_PIXELSORT_AXIS", "x"),
        sort_key=os.environ.get("TILESTITCH_PIXELSORT_KEY", "brightness"),
        threshold_low=float(os.environ.get("TILESTITCH_PIXELSORT_LOW", "0.2")),
        threshold_high=float(os.environ.get("TILESTITCH_PIXELSORT_HIGH", "0.8")),
        reverse=os.environ.get("TILESTITCH_PIXELSORT_REVERSE", "false").lower() == "true",
    )
