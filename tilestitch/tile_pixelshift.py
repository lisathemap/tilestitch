"""Pixel shift (channel offset) effect for map tiles."""
from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image


class PixelShiftError(Exception):
    """Raised when pixel shift configuration or application fails."""


@dataclass
class PixelShiftConfig:
    """Configuration for the pixel shift effect.

    Attributes:
        x_shift: Horizontal pixel offset applied to the red channel.
        y_shift: Vertical pixel offset applied to the blue channel.
        enabled: Whether the effect is active.
    """

    x_shift: int = 4
    y_shift: int = 0
    enabled: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.x_shift, int):
            raise PixelShiftError("x_shift must be an integer")
        if not isinstance(self.y_shift, int):
            raise PixelShiftError("y_shift must be an integer")
        if self.x_shift == 0 and self.y_shift == 0:
            raise PixelShiftError("at least one of x_shift or y_shift must be non-zero")


def pixelshift_config_from_env() -> PixelShiftConfig:
    """Build a PixelShiftConfig from environment variables."""
    enabled = os.environ.get("TILESTITCH_PIXELSHIFT_ENABLED", "true").strip().lower() != "false"
    try:
        x_shift = int(os.environ.get("TILESTITCH_PIXELSHIFT_X", "4"))
    except ValueError as exc:
        raise PixelShiftError("TILESTITCH_PIXELSHIFT_X must be an integer") from exc
    try:
        y_shift = int(os.environ.get("TILESTITCH_PIXELSHIFT_Y", "0"))
    except ValueError as exc:
        raise PixelShiftError("TILESTITCH_PIXELSHIFT_Y must be an integer") from exc
    return PixelShiftConfig(x_shift=x_shift, y_shift=y_shift, enabled=enabled)


def apply_pixelshift(image: Image.Image, config: PixelShiftConfig) -> Image.Image:
    """Apply a channel-level pixel shift to *image*.

    The red channel is shifted by (+x_shift, +y_shift) and the blue channel
    by (-x_shift, -y_shift), producing a colour-fringe / glitch appearance.
    """
    rgba = image.convert("RGBA")
    r, g, b, a = rgba.split()

    def _shift(channel: Image.Image, dx: int, dy: int) -> Image.Image:
        shifted = Image.new("L", channel.size, 0)
        shifted.paste(channel, (dx, dy))
        return shifted

    r_shifted = _shift(r, config.x_shift, config.y_shift)
    b_shifted = _shift(b, -config.x_shift, -config.y_shift)

    result = Image.merge("RGBA", (r_shifted, g, b_shifted, a))
    return result.convert(image.mode)
