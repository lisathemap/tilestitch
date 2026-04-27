"""Scanline overlay effect for tiles."""
from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image, ImageDraw


class ScanlinesError(ValueError):
    """Raised when scanline configuration is invalid."""


def _bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes")


@dataclass
class ScanlinesConfig:
    """Configuration for the scanlines effect."""

    enabled: bool = True
    line_spacing: int = 4
    opacity: float = 0.3
    colour: str = "#000000"

    def __post_init__(self) -> None:
        if self.line_spacing < 1:
            raise ScanlinesError("line_spacing must be at least 1")
        if not (0.0 <= self.opacity <= 1.0):
            raise ScanlinesError("opacity must be between 0.0 and 1.0")
        if not self.colour.strip():
            raise ScanlinesError("colour must not be empty")


def scanlines_config_from_env() -> ScanlinesConfig:
    """Build a ScanlinesConfig from environment variables."""
    kwargs: dict = {}
    if (v := os.environ.get("TILESTITCH_SCANLINES_ENABLED")) is not None:
        kwargs["enabled"] = _bool(v)
    if (v := os.environ.get("TILESTITCH_SCANLINES_SPACING")) is not None:
        kwargs["line_spacing"] = int(v)
    if (v := os.environ.get("TILESTITCH_SCANLINES_OPACITY")) is not None:
        kwargs["opacity"] = float(v)
    if (v := os.environ.get("TILESTITCH_SCANLINES_COLOUR")) is not None:
        kwargs["colour"] = v.strip()
    return ScanlinesConfig(**kwargs)


def apply_scanlines(image: Image.Image, config: ScanlinesConfig) -> Image.Image:
    """Overlay horizontal scanlines on *image*."""
    if not config.enabled:
        return image

    base = image.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        r, g, b = Image.new("RGB", (1, 1), config.colour).getpixel((0, 0))
    except (ValueError, AttributeError) as exc:
        raise ScanlinesError(f"invalid colour '{config.colour}': {exc}") from exc

    alpha = int(round(config.opacity * 255))
    width, height = base.size
    y = 0
    while y < height:
        draw.line([(0, y), (width - 1, y)], fill=(r, g, b, alpha))
        y += config.line_spacing

    result = Image.alpha_composite(base, overlay)
    if image.mode != "RGBA":
        result = result.convert(image.mode)
    return result
