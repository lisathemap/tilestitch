from __future__ import annotations

from dataclasses import dataclass
from PIL import Image, ImageEnhance


class ContrastError(ValueError):
    """Raised when contrast configuration is invalid."""


@dataclass
class ContrastConfig:
    enabled: bool = False
    factor: float = 1.0  # 1.0 = original, <1 less, >1 more

    def __post_init__(self) -> None:
        if self.factor <= 0:
            raise ContrastError(f"factor must be positive, got {self.factor}")


def contrast_config_from_env() -> ContrastConfig:
    import os

    enabled = os.environ.get("TILESTITCH_CONTRAST_ENABLED", "false").lower() == "true"
    raw_factor = os.environ.get("TILESTITCH_CONTRAST_FACTOR", "1.0")
    try:
        factor = float(raw_factor)
    except ValueError:
        raise ContrastError(
            f"TILESTITCH_CONTRAST_FACTOR must be a number, got {raw_factor!r}"
        )
    return ContrastConfig(enabled=enabled, factor=factor)


def adjust_contrast(image: Image.Image, config: ContrastConfig) -> Image.Image:
    """Return a contrast-adjusted copy of *image*."""
    if not config.enabled or config.factor == 1.0:
        return image
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(config.factor)
