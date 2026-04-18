from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image


class OpacityError(ValueError):
    pass


@dataclass
class OpacityConfig:
    enabled: bool = True
    alpha: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.alpha <= 1.0:
            raise OpacityError(f"alpha must be between 0.0 and 1.0, got {self.alpha}")


def opacity_config_from_env() -> OpacityConfig:
    enabled = os.environ.get("TILESTITCH_OPACITY_ENABLED", "true").strip().lower() != "false"
    alpha = float(os.environ.get("TILESTITCH_OPACITY_ALPHA", "1.0"))
    return OpacityConfig(enabled=enabled, alpha=alpha)


def apply_opacity(image: Image.Image, config: OpacityConfig) -> Image.Image:
    """Return a copy of *image* with uniform alpha scaled by *config.alpha*."""
    if not config.enabled or config.alpha == 1.0:
        return image

    rgba = image.convert("RGBA")
    r, g, b, a = rgba.split()
    a = a.point(lambda v: int(v * config.alpha))
    return Image.merge("RGBA", (r, g, b, a))
