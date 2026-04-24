"""Despeckle (median-filter) post-processing for stitched tiles."""

from __future__ import annotations

from dataclasses import dataclass
from PIL import Image, ImageFilter


class DespeckleError(Exception):
    """Raised when despeckle configuration or processing fails."""


@dataclass
class DespeckleConfig:
    """Configuration for the despeckle filter."""

    enabled: bool = True
    iterations: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise DespeckleError("enabled must be a bool")
        if self.iterations < 1:
            raise DespeckleError("iterations must be >= 1")


def despeckle_config_from_env(env: dict[str, str] | None = None) -> DespeckleConfig:
    """Build a DespeckleConfig from environment variables.

    Recognised variables:
      TILESTITCH_DESPECKLE_ENABLED   – '1' / 'true' to enable (default: true)
      TILESTITCH_DESPECKLE_ITERATIONS – positive integer (default: 1)
    """
    import os

    if env is None:
        env = dict(os.environ)

    def _bool(val: str) -> bool:
        return val.strip().lower() in ("1", "true", "yes")

    enabled = _bool(env.get("TILESTITCH_DESPECKLE_ENABLED", "true"))
    try:
        iterations = int(env.get("TILESTITCH_DESPECKLE_ITERATIONS", "1"))
    except ValueError as exc:
        raise DespeckleError("TILESTITCH_DESPECKLE_ITERATIONS must be an integer") from exc

    return DespeckleConfig(enabled=enabled, iterations=iterations)


def apply_despeckle(image: Image.Image, config: DespeckleConfig) -> Image.Image:
    """Apply median-based despeckle to *image* according to *config*."""
    if not config.enabled:
        return image

    result = image.convert("RGBA")
    for _ in range(config.iterations):
        result = result.filter(ImageFilter.MedianFilter(size=3))
    return result
