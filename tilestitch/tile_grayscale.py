"""Grayscale conversion pipeline stage for stitched tile images."""
from __future__ import annotations

from dataclasses import dataclass
from PIL import Image
import os


class GrayscaleError(Exception):
    """Raised when grayscale conversion fails."""


@dataclass
class GrayscaleConfig:
    enabled: bool = False
    keep_alpha: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise GrayscaleError("enabled must be a bool")
        if not isinstance(self.keep_alpha, bool):
            raise GrayscaleError("keep_alpha must be a bool")


def grayscale_config_from_env() -> GrayscaleConfig:
    enabled = os.environ.get("TILESTITCH_GRAYSCALE", "false").strip().lower() == "true"
    keep_alpha = os.environ.get("TILESTITCH_GRAYSCALE_KEEP_ALPHA", "true").strip().lower() != "false"
    return GrayscaleConfig(enabled=enabled, keep_alpha=keep_alpha)


def convert_to_grayscale(image: Image.Image, config: GrayscaleConfig) -> Image.Image:
    """Return a grayscale version of *image* according to *config*."""
    if not config.enabled:
        return image

    if image.mode not in ("RGB", "RGBA", "L", "LA", "P"):
        raise GrayscaleError(f"Unsupported image mode for grayscale conversion: {image.mode}")

    has_alpha = image.mode in ("RGBA", "LA")

    if has_alpha and config.keep_alpha:
        # Split alpha, convert colour channels, reattach alpha
        if image.mode == "RGBA":
            r, g, b, a = image.split()
            grey = Image.merge("RGB", (r, g, b)).convert("L")
            return Image.merge("LA", (grey, a))
        else:  # LA
            l_ch, a = image.split()
            return Image.merge("LA", (l_ch, a))

    return image.convert("L")


@dataclass
class GrayscaleStage:
    config: GrayscaleConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return convert_to_grayscale(image, self.config)


def build_grayscale_stage(config: GrayscaleConfig | None = None) -> GrayscaleStage:
    if config is None:
        config = grayscale_config_from_env()
    return GrayscaleStage(config=config)
