"""Colour inversion filter for stitched tile images."""
from __future__ import annotations

from dataclasses import dataclass
from PIL import Image, ImageOps


class InvertError(Exception):
    """Raised when inversion cannot be applied."""


@dataclass
class InvertConfig:
    enabled: bool = False
    preserve_alpha: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise InvertError("enabled must be a bool")
        if not isinstance(self.preserve_alpha, bool):
            raise InvertError("preserve_alpha must be a bool")


def invert_config_from_env() -> InvertConfig:
    import os

    def _bool(val: str) -> bool:
        return val.strip().lower() in ("1", "true", "yes")

    enabled = _bool(os.environ.get("TILESTITCH_INVERT_ENABLED", "false"))
    preserve_alpha = _bool(
        os.environ.get("TILESTITCH_INVERT_PRESERVE_ALPHA", "true")
    )
    return InvertConfig(enabled=enabled, preserve_alpha=preserve_alpha)


def apply_invert(image: Image.Image, config: InvertConfig) -> Image.Image:
    """Invert pixel colours, optionally preserving the alpha channel."""
    if not config.enabled:
        return image

    if image.mode == "RGBA" and config.preserve_alpha:
        r, g, b, a = image.split()
        rgb = Image.merge("RGB", (r, g, b))
        inverted_rgb = ImageOps.invert(rgb)
        ri, gi, bi = inverted_rgb.split()
        return Image.merge("RGBA", (ri, gi, bi, a))

    if image.mode != "RGB":
        image = image.convert("RGB")

    return ImageOps.invert(image)
