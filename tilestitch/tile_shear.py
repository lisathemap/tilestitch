"""Shear (skew) transformation for stitched map images."""
from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image


class ShearError(Exception):
    """Raised when shear configuration or application fails."""


@dataclass
class ShearConfig:
    """Configuration for shear transformation.

    Attributes:
        x_shear: Horizontal shear factor (default 0.0 = no shear).
        y_shear: Vertical shear factor (default 0.0 = no shear).
        enabled: Whether shear is active.
        fill_colour: Background fill colour for exposed areas.
    """

    x_shear: float = 0.0
    y_shear: float = 0.0
    enabled: bool = True
    fill_colour: tuple[int, int, int, int] = (0, 0, 0, 0)

    def __post_init__(self) -> None:
        if not -1.0 <= self.x_shear <= 1.0:
            raise ShearError("x_shear must be in the range [-1.0, 1.0]")
        if not -1.0 <= self.y_shear <= 1.0:
            raise ShearError("y_shear must be in the range [-1.0, 1.0]")


def shear_config_from_env() -> ShearConfig:
    """Build a ShearConfig from environment variables.

    Variables:
        TILESTITCH_SHEAR_X       – horizontal shear factor (default 0.0)
        TILESTITCH_SHEAR_Y       – vertical shear factor (default 0.0)
        TILESTITCH_SHEAR_ENABLED – 'true'/'false' (default 'true')
        TILESTITCH_SHEAR_FILL    – RGBA fill as 'R,G,B,A' (default '0,0,0,0')
    """
    x = float(os.environ.get("TILESTITCH_SHEAR_X", "0.0"))
    y = float(os.environ.get("TILESTITCH_SHEAR_Y", "0.0"))
    enabled = os.environ.get("TILESTITCH_SHEAR_ENABLED", "true").strip().lower() == "true"
    fill_raw = os.environ.get("TILESTITCH_SHEAR_FILL", "0,0,0,0")
    parts = [int(v.strip()) for v in fill_raw.split(",")]
    if len(parts) != 4:
        raise ShearError("TILESTITCH_SHEAR_FILL must be 'R,G,B,A'")
    fill = tuple(parts)  # type: ignore[assignment]
    return ShearConfig(x_shear=x, y_shear=y, enabled=enabled, fill_colour=fill)


def apply_shear(image: Image.Image, config: ShearConfig) -> Image.Image:
    """Apply an affine shear transformation to *image*.

    The output canvas expands to contain the full sheared image so that no
    pixel data is clipped.
    """
    if not config.enabled:
        return image
    if config.x_shear == 0.0 and config.y_shear == 0.0:
        return image

    w, h = image.size
    sx = config.x_shear
    sy = config.y_shear

    # New canvas dimensions to avoid clipping.
    new_w = int(w + abs(sx) * h)
    new_h = int(h + abs(sy) * w)

    # Offset so that the sheared image stays centred.
    tx = int(abs(sx) * h / 2)
    ty = int(abs(sy) * w / 2)

    # PIL affine transform: (a, b, c, d, e, f) maps output -> input.
    # For shear: x' = x + sx*y, y' = sy*x + y
    # Inverse: x = x' - sx*(y' - ty) - tx, y = y' - sy*(x' - tx) - ty
    transform = (1, sx, -(tx + sx * ty), sy, 1, -(ty + sy * tx))

    rgba = image.convert("RGBA")
    out = rgba.transform(
        (new_w, new_h),
        Image.AFFINE,
        transform,
        resample=Image.BILINEAR,
        fillcolor=config.fill_colour,
    )
    return out
