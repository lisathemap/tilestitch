"""Tone-level adjustment (black point / white point / midtone gamma)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image, ImageOps


class LevelsError(ValueError):
    """Raised when a LevelsConfig value is invalid."""


@dataclass
class LevelsConfig:
    """Parameters for a levels adjustment.

    Attributes:
        in_low:   Input black point  (0–254).
        in_high:  Input white point  (1–255, must be > in_low).
        gamma:    Midtone correction (> 0; 1.0 = no change).
        out_low:  Output black point (0–254).
        out_high: Output white point (1–255, must be > out_low).
        enabled:  When False the stage is a no-op.
    """

    in_low: int = 0
    in_high: int = 255
    gamma: float = 1.0
    out_low: int = 0
    out_high: int = 255
    enabled: bool = True

    def __post_init__(self) -> None:
        if not (0 <= self.in_low <= 254):
            raise LevelsError("in_low must be in [0, 254]")
        if not (1 <= self.in_high <= 255):
            raise LevelsError("in_high must be in [1, 255]")
        if self.in_high <= self.in_low:
            raise LevelsError("in_high must be greater than in_low")
        if self.gamma <= 0:
            raise LevelsError("gamma must be > 0")
        if not (0 <= self.out_low <= 254):
            raise LevelsError("out_low must be in [0, 254]")
        if not (1 <= self.out_high <= 255):
            raise LevelsError("out_high must be in [1, 255]")
        if self.out_high <= self.out_low:
            raise LevelsError("out_high must be greater than out_low")


def levels_config_from_env() -> LevelsConfig:
    """Build a :class:`LevelsConfig` from environment variables.

    Variables read (all optional):
        TILESTITCH_LEVELS_IN_LOW, TILESTITCH_LEVELS_IN_HIGH,
        TILESTITCH_LEVELS_GAMMA,
        TILESTITCH_LEVELS_OUT_LOW, TILESTITCH_LEVELS_OUT_HIGH,
        TILESTITCH_LEVELS_ENABLED
    """
    return LevelsConfig(
        in_low=int(os.environ.get("TILESTITCH_LEVELS_IN_LOW", 0)),
        in_high=int(os.environ.get("TILESTITCH_LEVELS_IN_HIGH", 255)),
        gamma=float(os.environ.get("TILESTITCH_LEVELS_GAMMA", 1.0)),
        out_low=int(os.environ.get("TILESTITCH_LEVELS_OUT_LOW", 0)),
        out_high=int(os.environ.get("TILESTITCH_LEVELS_OUT_HIGH", 255)),
        enabled=os.environ.get("TILESTITCH_LEVELS_ENABLED", "true").lower() != "false",
    )


def apply_levels(image: Image.Image, config: LevelsConfig) -> Image.Image:
    """Apply a levels adjustment to *image*.

    The image is first auto-levelled within the input range, then a gamma
    correction is applied, and finally the output is mapped to the output range.
    """
    if not config.enabled:
        return image

    img = image.convert("RGBA") if image.mode == "RGBA" else image.convert("RGB")
    has_alpha = image.mode == "RGBA"

    # Split alpha channel so it is not affected by colour operations.
    if has_alpha:
        r, g, b, a = img.split()
        rgb = Image.merge("RGB", (r, g, b))
    else:
        rgb = img
        a = None

    # Map input range → full range, apply gamma, map to output range.
    rgb = ImageOps.level(rgb, (config.in_low, config.in_high), config.gamma,
                         (config.out_low, config.out_high))

    if has_alpha:
        r2, g2, b2 = rgb.split()
        result = Image.merge("RGBA", (r2, g2, b2, a))
    else:
        result = rgb

    return result
