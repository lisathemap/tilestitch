from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image, ImageEnhance


class SaturationError(Exception):
    pass


@dataclass
class SaturationConfig:
    factor: float = 1.0
    enabled: bool = True

    def __post_init__(self) -> None:
        if self.factor < 0:
            raise SaturationError("factor must be >= 0")


def saturation_config_from_env() -> SaturationConfig:
    factor = float(os.environ.get("TILESTITCH_SATURATION_FACTOR", "1.0"))
    enabled_raw = os.environ.get("TILESTITCH_SATURATION_ENABLED", "true").strip().lower()
    if enabled_raw not in ("true", "false", "1", "0"):
        raise SaturationError(f"invalid enabled value: {enabled_raw!r}")
    enabled = enabled_raw in ("true", "1")
    return SaturationConfig(factor=factor, enabled=enabled)


def apply_saturation(image: Image.Image, config: SaturationConfig) -> Image.Image:
    if not config.enabled:
        return image
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(config.factor)
