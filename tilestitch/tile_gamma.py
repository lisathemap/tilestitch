"""Gamma correction for stitched tile images."""
from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image
import numpy as np


class GammaError(Exception):
    """Raised when gamma configuration or application fails."""


@dataclass
class GammaConfig:
    enabled: bool = True
    gamma: float = 1.0

    def __post_init__(self) -> None:
        if self.gamma <= 0:
            raise GammaError(f"gamma must be positive, got {self.gamma}")
        if self.gamma == 0:
            raise GammaError("gamma must not be zero")


def gamma_config_from_env() -> GammaConfig:
    enabled = os.environ.get("TILESTITCH_GAMMA_ENABLED", "true").strip().lower() != "false"
    try:
        gamma = float(os.environ.get("TILESTITCH_GAMMA", "1.0"))
    except ValueError as exc:
        raise GammaError(f"Invalid TILESTITCH_GAMMA value: {exc}") from exc
    return GammaConfig(enabled=enabled, gamma=gamma)


def apply_gamma(image: Image.Image, config: GammaConfig) -> Image.Image:
    """Apply gamma correction to *image* and return a new image."""
    if not config.enabled or config.gamma == 1.0:
        return image

    mode = image.mode
    img = image.convert("RGBA") if mode == "P" else image

    arr = np.array(img, dtype=np.float32)

    if img.mode in ("RGBA", "LA"):
        alpha = arr[..., -1:].copy()
        colour = arr[..., :-1]
        colour = np.clip((colour / 255.0) ** (1.0 / config.gamma) * 255.0, 0, 255)
        arr = np.concatenate([colour, alpha], axis=-1)
    else:
        arr = np.clip((arr / 255.0) ** (1.0 / config.gamma) * 255.0, 0, 255)

    result = Image.fromarray(arr.astype(np.uint8), mode=img.mode)
    return result.convert(mode) if mode == "P" else result
