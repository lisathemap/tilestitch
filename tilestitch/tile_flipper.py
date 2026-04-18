"""Flip (mirror) a stitched image horizontally or vertically."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from PIL import Image


class FlipError(ValueError):
    """Raised when flip configuration is invalid."""


class FlipAxis(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    BOTH = "both"

    @staticmethod
    def from_string(value: str) -> "FlipAxis":
        normalised = value.strip().lower()
        for member in FlipAxis:
            if member.value == normalised:
                return member
        raise FlipError(
            f"Unknown flip axis {value!r}. Choose from: "
            + ", ".join(m.value for m in FlipAxis)
        )


@dataclass
class FlipConfig:
    enabled: bool = False
    axis: FlipAxis = FlipAxis.HORIZONTAL

    def __post_init__(self) -> None:
        if not isinstance(self.axis, FlipAxis):
            raise FlipError("axis must be a FlipAxis instance")


def flip_config_from_env() -> FlipConfig:
    import os

    raw_enabled = os.environ.get("TILESTITCH_FLIP_ENABLED", "false").strip().lower()
    enabled = raw_enabled in ("1", "true", "yes")
    raw_axis = os.environ.get("TILESTITCH_FLIP_AXIS", "horizontal")
    axis = FlipAxis.from_string(raw_axis)
    return FlipConfig(enabled=enabled, axis=axis)


def flip_image(image: Image.Image, config: FlipConfig) -> Image.Image:
    """Return a flipped copy of *image* according to *config*."""
    if not config.enabled:
        return image
    if config.axis is FlipAxis.HORIZONTAL:
        return image.transpose(Image.FLIP_LEFT_RIGHT)
    if config.axis is FlipAxis.VERTICAL:
        return image.transpose(Image.FLIP_TOP_BOTTOM)
    # BOTH
    return image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
