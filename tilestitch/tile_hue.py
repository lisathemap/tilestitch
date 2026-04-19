from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image
from PIL.ImageEnhance import Color


class HueError(Exception):
    """Raised when hue shift configuration is invalid."""


@dataclass
class HueConfig:
    enabled: bool = True
    factor: float = 1.0  # 0.0 = grayscale, 1.0 = original, >1.0 = saturated

    def __post_init__(self) -> None:
        if self.factor < 0.0:
            raise HueError(f"factor must be >= 0.0, got {self.factor}")


def hue_config_from_env() -> HueConfig:
    enabled = os.environ.get("TILESTITCH_HUE_ENABLED", "true").strip().lower() != "false"
    factor = float(os.environ.get("TILESTITCH_HUE_FACTOR", "1.0"))
    return HueConfig(enabled=enabled, factor=factor)


def apply_hue(image: Image.Image, config: HueConfig) -> Image.Image:
    """Adjust colour saturation of *image* using *config.factor*.

    A factor of 1.0 returns the original image unchanged.
    A factor of 0.0 produces a grayscale image.
    Values above 1.0 increase saturation.
    """
    if not config.enabled:
        return image
    if config.factor == 1.0:
        return image
    enhancer = Color(image)
    return enhancer.enhance(config.factor)
