"""Colour quantization for stitched tile images."""
from __future__ import annotations

import os
from dataclasses import dataclass
from PIL import Image


class QuantizeError(ValueError):
    """Raised when quantization configuration is invalid."""


@dataclass
class QuantizeConfig:
    enabled: bool = False
    colours: int = 256
    dither: bool = True

    def __post_init__(self) -> None:
        if self.colours < 2:
            raise QuantizeError("colours must be >= 2")
        if self.colours > 256:
            raise QuantizeError("colours must be <= 256")


def quantize_config_from_env() -> QuantizeConfig:
    enabled = os.getenv("TILESTITCH_QUANTIZE_ENABLED", "false").strip().lower() == "true"
    colours = int(os.getenv("TILESTITCH_QUANTIZE_COLOURS", "256"))
    dither = os.getenv("TILESTITCH_QUANTIZE_DITHER", "true").strip().lower() != "false"
    return QuantizeConfig(enabled=enabled, colours=colours, dither=dither)


def apply_quantize(image: Image.Image, config: QuantizeConfig) -> Image.Image:
    """Reduce the number of colours in *image* using palette quantization."""
    if not config.enabled:
        return image

    dither_flag = Image.Dither.FLOYDSTEINBERG if config.dither else Image.Dither.NONE

    original_mode = image.mode
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")
        original_mode = "RGB"

    quantized = image.quantize(colors=config.colours, dither=dither_flag)
    result = quantized.convert(original_mode)
    return result
