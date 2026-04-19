"""Sketch (pencil drawing) effect for stitched map tiles."""
from __future__ import annotations

from dataclasses import dataclass
from PIL import Image, ImageFilter, ImageOps


class SketchError(ValueError):
    """Raised when sketch configuration is invalid."""


@dataclass
class SketchConfig:
    enabled: bool = True
    blend: float = 0.8  # 0.0 = original, 1.0 = full sketch

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise SketchError("enabled must be a bool")
        if not (0.0 <= self.blend <= 1.0):
            raise SketchError("blend must be between 0.0 and 1.0")


def sketch_config_from_env() -> SketchConfig:
    import os

    enabled = os.environ.get("TILESTITCH_SKETCH_ENABLED", "false").strip().lower() == "true"
    blend = float(os.environ.get("TILESTITCH_SKETCH_BLEND", "0.8"))
    return SketchConfig(enabled=enabled, blend=blend)


def apply_sketch(image: Image.Image, config: SketchConfig) -> Image.Image:
    """Apply a pencil-sketch effect by inverting a blurred grayscale layer."""
    if not config.enabled:
        return image

    grey = ImageOps.grayscale(image)
    inverted = ImageOps.invert(grey)
    blurred = inverted.filter(ImageFilter.GaussianBlur(radius=21))

    # Dodge blend: grey / (1 - blurred)
    grey_f = grey.convert("F")
    blur_f = blurred.convert("F")

    import PIL.ImageChops as chops
    import PIL.ImageMath as imath

    sketch_f = imath.eval(
        "convert(min(g * 255.0 / max(255.0 - b, 1.0), 255.0), 'L')",
        g=grey_f,
        b=blur_f,
    )
    sketch = sketch_f.convert("RGB")

    base = image.convert("RGB")
    result = Image.blend(base, sketch, alpha=config.blend)

    if image.mode == "RGBA":
        result = result.convert("RGBA")
    return result
