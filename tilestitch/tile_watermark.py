"""Watermark overlay support for stitched map images."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
import os

from PIL import Image, ImageDraw, ImageFont


class WatermarkError(ValueError):
    pass


@dataclass
class WatermarkConfig:
    text: str
    opacity: float = 0.5
    font_size: int = 14
    colour: Tuple[int, int, int] = (255, 255, 255)
    position: str = "bottom-right"  # top-left, top-right, bottom-left, bottom-right
    margin: int = 8

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise WatermarkError("Watermark text must not be empty.")
        if not (0.0 < self.opacity <= 1.0):
            raise WatermarkError("opacity must be in range (0, 1].")
        if self.font_size < 6:
            raise WatermarkError("font_size must be at least 6.")
        valid = {"top-left", "top-right", "bottom-left", "bottom-right"}
        if self.position not in valid:
            raise WatermarkError(f"position must be one of {valid}.")
        if self.margin < 0:
            raise WatermarkError("margin must be non-negative.")


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def apply_watermark(image: Image.Image, config: WatermarkConfig) -> Image.Image:
    """Return a copy of *image* with the watermark applied."""
    out = image.convert("RGBA")
    overlay = Image.new("RGBA", out.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _get_font(config.font_size)

    bbox = draw.textbbox((0, 0), config.text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    w, h = out.size
    m = config.margin

    if config.position == "top-left":
        xy = (m, m)
    elif config.position == "top-right":
        xy = (w - tw - m, m)
    elif config.position == "bottom-left":
        xy = (m, h - th - m)
    else:
        xy = (w - tw - m, h - th - m)

    alpha = int(255 * config.opacity)
    r, g, b = config.colour
    draw.text(xy, config.text, font=font, fill=(r, g, b, alpha))
    return Image.alpha_composite(out, overlay).convert(image.mode)


def watermark_config_from_env() -> WatermarkConfig:
    return WatermarkConfig(
        text=os.environ.get("TILESTITCH_WATERMARK_TEXT", "tilestitch"),
        opacity=float(os.environ.get("TILESTITCH_WATERMARK_OPACITY", "0.5")),
        font_size=int(os.environ.get("TILESTITCH_WATERMARK_FONT_SIZE", "14")),
        position=os.environ.get("TILESTITCH_WATERMARK_POSITION", "bottom-right"),
        margin=int(os.environ.get("TILESTITCH_WATERMARK_MARGIN", "8")),
    )
