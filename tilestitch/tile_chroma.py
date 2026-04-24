"""Chroma key (green-screen) replacement for tiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
import os

from PIL import Image


class ChromaError(Exception):
    """Raised when chroma key configuration or processing fails."""


def _parse_colour(value: str) -> Tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise ChromaError(f"Invalid hex colour: #{value}")
    try:
        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)
    except ValueError:
        raise ChromaError(f"Invalid hex colour: #{value}")
    return r, g, b


@dataclass
class ChromaConfig:
    key_colour: str = "#00ff00"
    replacement_colour: str = "#ffffff"
    threshold: int = 30
    enabled: bool = True

    def __post_init__(self) -> None:
        _parse_colour(self.key_colour)  # validate
        _parse_colour(self.replacement_colour)  # validate
        if self.threshold < 0 or self.threshold > 255:
            raise ChromaError("threshold must be between 0 and 255")

    @property
    def key_rgb(self) -> Tuple[int, int, int]:
        return _parse_colour(self.key_colour)

    @property
    def replacement_rgb(self) -> Tuple[int, int, int]:
        return _parse_colour(self.replacement_colour)


def chroma_config_from_env() -> ChromaConfig:
    """Build a ChromaConfig from environment variables."""
    return ChromaConfig(
        key_colour=os.environ.get("TILESTITCH_CHROMA_KEY", "#00ff00"),
        replacement_colour=os.environ.get("TILESTITCH_CHROMA_REPLACEMENT", "#ffffff"),
        threshold=int(os.environ.get("TILESTITCH_CHROMA_THRESHOLD", "30")),
        enabled=os.environ.get("TILESTITCH_CHROMA_ENABLED", "true").lower() == "true",
    )


def apply_chroma(image: Image.Image, config: ChromaConfig) -> Image.Image:
    """Replace pixels close to the key colour with the replacement colour."""
    if not config.enabled:
        return image

    img = image.convert("RGBA")
    kr, kg, kb = config.key_rgb
    rr, rg, rb = config.replacement_rgb
    threshold = config.threshold
    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if (
                abs(r - kr) <= threshold
                and abs(g - kg) <= threshold
                and abs(b - kb) <= threshold
            ):
                pixels[x, y] = (rr, rg, rb, a)

    return img
