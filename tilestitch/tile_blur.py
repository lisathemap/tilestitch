from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image, ImageFilter


class BlurError(Exception):
    """Raised when blur configuration or application fails."""


@dataclass
class BlurConfig:
    enabled: bool = False
    radius: float = 1.0

    def __post_init__(self) -> None:
        if self.radius <= 0:
            raise BlurError(f"radius must be positive, got {self.radius}")


def blur_config_from_env() -> BlurConfig:
    enabled = os.environ.get("TILESTITCH_BLUR_ENABLED", "false").strip().lower() == "true"
    radius = float(os.environ.get("TILESTITCH_BLUR_RADIUS", "1.0"))
    return BlurConfig(enabled=enabled, radius=radius)


def apply_blur(image: Image.Image, config: BlurConfig) -> Image.Image:
    """Return a blurred copy of *image* using a Gaussian kernel."""
    if not config.enabled:
        return image
    return image.filter(ImageFilter.GaussianBlur(radius=config.radius))
