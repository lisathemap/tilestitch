"""Histogram equalisation / stretching for stitched tiles."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from PIL import Image, ImageOps


class HistogramError(ValueError):
    """Raised when histogram configuration is invalid."""


_MODES: frozenset[str] = frozenset({"equalize", "stretch"})


@dataclass
class HistogramConfig:
    enabled: bool = False
    mode: str = "equalize"  # 'equalize' | 'stretch'

    def __post_init__(self) -> None:
        mode = self.mode.strip().lower()
        if mode not in _MODES:
            raise HistogramError(
                f"Invalid histogram mode {self.mode!r}. Choose from: {sorted(_MODES)}"
            )
        self.mode = mode


def histogram_config_from_env() -> HistogramConfig:
    """Build a HistogramConfig from environment variables."""
    import os

    enabled = os.environ.get("TILESTITCH_HISTOGRAM_ENABLED", "false").strip().lower() == "true"
    mode = os.environ.get("TILESTITCH_HISTOGRAM_MODE", "equalize").strip().lower()
    return HistogramConfig(enabled=enabled, mode=mode)


def apply_histogram(image: Image.Image, config: HistogramConfig) -> Image.Image:
    """Apply histogram equalisation or stretching to *image*."""
    if not config.enabled:
        return image

    original_mode = image.mode
    working = image.convert("RGB") if image.mode not in ("RGB", "L") else image

    if config.mode == "equalize":
        result = ImageOps.equalize(working)
    elif config.mode == "stretch":
        result = ImageOps.autocontrast(working)
    else:  # pragma: no cover
        raise HistogramError(f"Unhandled mode: {config.mode!r}")

    if original_mode != working.mode:
        result = result.convert(original_mode)
    return result
