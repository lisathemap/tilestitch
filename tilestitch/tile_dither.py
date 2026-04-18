"""Dithering effect for stitched map tiles."""

from __future__ import annotations

from dataclasses import dataclass
from PIL import Image
import os


class DitherError(ValueError):
    """Raised when dither configuration is invalid."""


_VALID_MODES = {"floydsteinberg", "ordered", "none"}


@dataclass
class DitherConfig:
    enabled: bool = False
    mode: str = "floydsteinberg"
    colours: int = 256

    def __post_init__(self) -> None:
        mode = self.mode.strip().lower()
        if mode not in _VALID_MODES:
            raise DitherError(
                f"Invalid dither mode {self.mode!r}. Choose from: {sorted(_VALID_MODES)}"
            )
        self.mode = mode
        if not (2 <= self.colours <= 256):
            raise DitherError("colours must be between 2 and 256")


def dither_config_from_env() -> DitherConfig:
    enabled = os.environ.get("TILESTITCH_DITHER_ENABLED", "false").lower() == "true"
    mode = os.environ.get("TILESTITCH_DITHER_MODE", "floydsteinberg")
    colours = int(os.environ.get("TILESTITCH_DITHER_COLOURS", "256"))
    return DitherConfig(enabled=enabled, mode=mode, colours=colours)


def apply_dither(image: Image.Image, config: DitherConfig) -> Image.Image:
    """Apply dithering to *image* according to *config*."""
    if not config.enabled or config.mode == "none":
        return image

    original_mode = image.mode
    if config.mode == "floydsteinberg":
        dither_flag = Image.Dither.FLOYDSTEINBERG
    else:
        dither_flag = Image.Dither.ORDERED

    quantized = image.convert("P", palette=Image.Palette.ADAPTIVE,
                              colors=config.colours, dither=dither_flag)
    return quantized.convert(original_mode)
