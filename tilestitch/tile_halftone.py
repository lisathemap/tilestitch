"""Halftone effect for tile images."""
from __future__ import annotations

import math
from dataclasses import dataclass
from PIL import Image, ImageDraw


class HalftoneError(Exception):
    """Raised when halftone configuration or processing fails."""


@dataclass
class HalftoneConfig:
    """Configuration for the halftone effect."""

    enabled: bool = True
    dot_size: int = 6
    angle: float = 45.0
    foreground: str = "#000000"
    background: str = "#ffffff"

    def __post_init__(self) -> None:
        if self.dot_size < 1:
            raise HalftoneError("dot_size must be at least 1")
        if not (0.0 <= self.angle < 360.0):
            raise HalftoneError("angle must be in [0, 360)")


def halftone_config_from_env() -> HalftoneConfig:
    """Build a HalftoneConfig from environment variables."""
    import os

    raw_enabled = os.environ.get("TILESTITCH_HALFTONE_ENABLED", "true")
    raw_dot = os.environ.get("TILESTITCH_HALFTONE_DOT_SIZE", "6")
    raw_angle = os.environ.get("TILESTITCH_HALFTONE_ANGLE", "45.0")
    fg = os.environ.get("TILESTITCH_HALFTONE_FG", "#000000")
    bg = os.environ.get("TILESTITCH_HALFTONE_BG", "#ffffff")

    enabled = raw_enabled.strip().lower() not in ("0", "false", "no")
    try:
        dot_size = int(raw_dot)
    except ValueError as exc:
        raise HalftoneError(f"Invalid dot_size: {raw_dot!r}") from exc
    try:
        angle = float(raw_angle)
    except ValueError as exc:
        raise HalftoneError(f"Invalid angle: {raw_angle!r}") from exc

    return HalftoneConfig(enabled=enabled, dot_size=dot_size, angle=angle,
                          foreground=fg, background=bg)


def apply_halftone(image: Image.Image, config: HalftoneConfig) -> Image.Image:
    """Apply a halftone effect to *image* and return the result."""
    if not config.enabled:
        return image

    src = image.convert("L")
    out = Image.new("RGB", image.size, config.background)
    draw = ImageDraw.Draw(out)

    w, h = image.size
    step = config.dot_size
    rad = math.radians(config.angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)

    for gy in range(-step, h + step, step):
        for gx in range(-step, w + step, step):
            rx = int(gx * cos_a - gy * sin_a)
            ry = int(gx * sin_a + gy * cos_a)
            if 0 <= rx < w and 0 <= ry < h:
                brightness = src.getpixel((rx, ry))
                radius = (step / 2) * (1.0 - brightness / 255.0)
                if radius > 0:
                    x0 = rx - radius
                    y0 = ry - radius
                    x1 = rx + radius
                    y1 = ry + radius
                    draw.ellipse([x0, y0, x1, y1], fill=config.foreground)

    return out
