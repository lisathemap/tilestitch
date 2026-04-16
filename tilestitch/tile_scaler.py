"""Tile scaling utilities for resampling tile images to a target resolution."""

from __future__ import annotations

from enum import Enum
from PIL import Image


class ScaleMethod(Enum):
    NEAREST = "nearest"
    BILINEAR = "bilinear"
    BICUBIC = "bicubic"
    LANCZOS = "lanczos"

    @classmethod
    def from_string(cls, value: str) -> "ScaleMethod":
        """Parse a ScaleMethod from a string, case-insensitive."""
        normalised = value.strip().lower()
        for member in cls:
            if member.value == normalised:
                return member
        valid = ", ".join(m.value for m in cls)
        raise ScaleMethodError(f"Unknown scale method {value!r}. Valid options: {valid}")

    def pil_resample(self) -> Image.Resampling:
        """Return the corresponding PIL resampling filter."""
        mapping = {
            ScaleMethod.NEAREST: Image.Resampling.NEAREST,
            ScaleMethod.BILINEAR: Image.Resampling.BILINEAR,
            ScaleMethod.BICUBIC: Image.Resampling.BICUBIC,
            ScaleMethod.LANCZOS: Image.Resampling.LANCZOS,
        }
        return mapping[self]


class ScaleMethodError(Exception):
    """Raised when an unrecognised scale method string is provided."""


def scale_tile(image: Image.Image, target_size: int, method: ScaleMethod = ScaleMethod.LANCZOS) -> Image.Image:
    """Scale a single tile image to *target_size* x *target_size* pixels.

    Args:
        image: Source PIL image.
        target_size: Desired width and height in pixels.
        method: Resampling algorithm to use.

    Returns:
        A new PIL Image scaled to (target_size, target_size).

    Raises:
        ValueError: If target_size is not a positive integer.
    """
    if target_size <= 0:
        raise ValueError(f"target_size must be a positive integer, got {target_size}")
    if image.size == (target_size, target_size):
        return image.copy()
    return image.resize((target_size, target_size), resample=method.pil_resample())


def scale_image(image: Image.Image, scale_factor: float, method: ScaleMethod = ScaleMethod.LANCZOS) -> Image.Image:
    """Scale a stitched image by an arbitrary factor.

    Args:
        image: Source PIL image (any size).
        scale_factor: Multiplier applied to both dimensions.
        method: Resampling algorithm to use.

    Returns:
        A new PIL Image with dimensions multiplied by scale_factor.

    Raises:
        ValueError: If scale_factor is not positive.
    """
    if scale_factor <= 0:
        raise ValueError(f"scale_factor must be positive, got {scale_factor}")
    new_w = max(1, round(image.width * scale_factor))
    new_h = max(1, round(image.height * scale_factor))
    return image.resize((new_w, new_h), resample=method.pil_resample())
