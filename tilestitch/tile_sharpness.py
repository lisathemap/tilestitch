"""Adaptive sharpness scoring for tiles using the Laplacian variance method."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from PIL import Image, ImageFilter


class SharpnessScoreError(Exception):
    """Raised when sharpness scoring fails."""


@dataclass
class SharpnessResult:
    """Holds the sharpness score and a blurry classification for a tile."""

    score: float
    is_blurry: bool
    threshold: float

    def __post_init__(self) -> None:
        if self.score < 0.0:
            raise SharpnessScoreError("score must be >= 0")
        if self.threshold <= 0.0:
            raise SharpnessScoreError("threshold must be > 0")


def _laplacian_variance(image: Image.Image) -> float:
    """Return variance of the Laplacian of *image* as a sharpness proxy."""
    grey = image.convert("L")
    lap = grey.filter(ImageFilter.Kernel(
        size=3,
        kernel=[0, 1, 0, 1, -4, 1, 0, 1, 0],
        scale=1,
        offset=128,
    ))
    pixels = list(lap.getdata())
    n = len(pixels)
    if n == 0:
        return 0.0
    mean = sum(pixels) / n
    variance = sum((p - mean) ** 2 for p in pixels) / n
    return variance


def score_sharpness(
    image: Image.Image,
    threshold: float = 100.0,
) -> SharpnessResult:
    """Score the sharpness of *image* and classify it against *threshold*.

    Args:
        image: A PIL Image to evaluate.
        threshold: Variance below which the tile is considered blurry.

    Returns:
        A :class:`SharpnessResult` with score, blurry flag, and threshold.
    """
    if not isinstance(image, Image.Image):
        raise SharpnessScoreError("image must be a PIL Image")
    if threshold <= 0.0:
        raise SharpnessScoreError("threshold must be > 0")
    variance = _laplacian_variance(image)
    return SharpnessResult(
        score=variance,
        is_blurry=variance < threshold,
        threshold=threshold,
    )


def sharpness_config_from_env() -> Tuple[bool, float]:
    """Return (enabled, threshold) from environment variables."""
    import os

    enabled = os.environ.get("TILESTITCH_SHARPNESS_ENABLED", "false").strip().lower() == "true"
    threshold = float(os.environ.get("TILESTITCH_SHARPNESS_THRESHOLD", "100.0"))
    return enabled, threshold
