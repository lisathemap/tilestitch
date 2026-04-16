"""Tile label rendering — draw tile coordinates or zoom level onto tile images."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from tilestitch.tile_math import TileBounds


@dataclass
class LabelConfig:
    enabled: bool = False
    color: Tuple[int, int, int, int] = (255, 0, 0, 200)
    font_size: int = 12
    show_zoom: bool = True
    show_coords: bool = True

    def __post_init__(self) -> None:
        if self.font_size < 6:
            raise ValueError("font_size must be at least 6")


def _get_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def label_tile(
    image: Image.Image,
    x: int,
    y: int,
    zoom: int,
    config: LabelConfig,
) -> Image.Image:
    """Return a copy of *image* with tile coordinate text rendered on it."""
    if not config.enabled:
        return image

    img = image.copy().convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _get_font(config.font_size)

    parts: list[str] = []
    if config.show_zoom:
        parts.append(f"z{zoom}")
    if config.show_coords:
        parts.append(f"{x},{y}")
    text = " ".join(parts)

    draw.text((4, 4), text, fill=config.color, font=font)
    return Image.alpha_composite(img, overlay).convert("RGB")


def label_config_from_env() -> LabelConfig:
    import os

    enabled = os.getenv("TILESTITCH_LABEL_TILES", "0") in ("1", "true", "yes")
    font_size = int(os.getenv("TILESTITCH_LABEL_FONT_SIZE", "12"))
    show_zoom = os.getenv("TILESTITCH_LABEL_SHOW_ZOOM", "1") not in ("0", "false", "no")
    show_coords = os.getenv("TILESTITCH_LABEL_SHOW_COORDS", "1") not in ("0", "false", "no")
    return LabelConfig(enabled=enabled, font_size=font_size, show_zoom=show_zoom, show_coords=show_coords)
