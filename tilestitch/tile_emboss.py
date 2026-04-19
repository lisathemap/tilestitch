from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image, ImageFilter


class EmbossError(Exception):
    """Raised when emboss configuration or application fails."""


@dataclass
class EmbossConfig:
    enabled: bool = True
    blend: float = 1.0  # 0.0 = original, 1.0 = full emboss

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise EmbossError("enabled must be a bool")
        if not (0.0 <= self.blend <= 1.0):
            raise EmbossError("blend must be between 0.0 and 1.0")


def emboss_config_from_env() -> EmbossConfig:
    enabled = os.environ.get("TILESTITCH_EMBOSS_ENABLED", "false").strip().lower() == "true"
    blend = float(os.environ.get("TILESTITCH_EMBOSS_BLEND", "1.0"))
    return EmbossConfig(enabled=enabled, blend=blend)


def apply_emboss(image: Image.Image, config: EmbossConfig) -> Image.Image:
    """Apply an emboss effect to *image*, blending with the original."""
    if not config.enabled:
        return image

    original = image.convert("RGBA")
    embossed = original.convert("RGB").filter(ImageFilter.EMBOSS).convert("RGBA")

    if config.blend >= 1.0:
        return embossed
    if config.blend <= 0.0:
        return original

    return Image.blend(original, embossed, config.blend)
