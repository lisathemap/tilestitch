"""Add borders/outlines to individual tiles."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import os

from PIL import Image, ImageDraw


class BorderError(ValueError):
    pass


@dataclass
class BorderConfig:
    width: int = 1
    colour: Tuple[int, int, int, int] = (255, 0, 0, 255)

    def __post_init__(self) -> None:
        if self.width < 1:
            raise BorderError(f"Border width must be >= 1, got {self.width}")
        if len(self.colour) != 4:
            raise BorderError("Colour must be an RGBA 4-tuple")
        for ch in self.colour:
            if not (0 <= ch <= 255):
                raise BorderError(f"Colour channel out of range: {ch}")


def add_border(image: Image.Image, config: BorderConfig) -> Image.Image:
    """Return a copy of *image* with a rectangular border drawn on it."""
    result = image.copy().convert("RGBA")
    draw = ImageDraw.Draw(result)
    w, h = result.size
    bw = config.width
    # top, bottom, left, right
    draw.rectangle([0, 0, w - 1, bw - 1], fill=config.colour)
    draw.rectangle([0, h - bw, w - 1, h - 1], fill=config.colour)
    draw.rectangle([0, 0, bw - 1, h - 1], fill=config.colour)
    draw.rectangle([w - bw, 0, w - 1, h - 1], fill=config.colour)
    return result


def border_config_from_env() -> BorderConfig:
    """Build a BorderConfig from environment variables.

    TILESTITCH_BORDER_WIDTH  – integer, default 1
    TILESTITCH_BORDER_COLOUR – R,G,B,A integers, default '255,0,0,255'
    """
    width = int(os.environ.get("TILESTITCH_BORDER_WIDTH", "1"))
    raw = os.environ.get("TILESTITCH_BORDER_COLOUR", "255,0,0,255")
    parts = [int(p.strip()) for p in raw.split(",")]
    if len(parts) != 4:
        raise BorderError("TILESTITCH_BORDER_COLOUR must have 4 comma-separated values")
    return BorderConfig(width=width, colour=tuple(parts))  # type: ignore[arg-type]
