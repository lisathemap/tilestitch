from __future__ import annotations

from dataclasses import dataclass
from PIL import Image, ImageFilter


class PencilError(Exception):
    """Raised when pencil sketch configuration or processing fails."""


@dataclass
class PencilConfig:
    enabled: bool = True
    blur_radius: float = 2.0
    blend: float = 0.85

    def __post_init__(self) -> None:
        if self.blur_radius <= 0:
            raise PencilError("blur_radius must be greater than zero")
        if not (0.0 <= self.blend <= 1.0):
            raise PencilError("blend must be between 0.0 and 1.0")


def pencil_config_from_env() -> PencilConfig:
    import os

    enabled = os.environ.get("TILESTITCH_PENCIL_ENABLED", "true").strip().lower() == "true"
    blur_radius = float(os.environ.get("TILESTITCH_PENCIL_BLUR_RADIUS", "2.0"))
    blend = float(os.environ.get("TILESTITCH_PENCIL_BLEND", "0.85"))
    return PencilConfig(enabled=enabled, blur_radius=blur_radius, blend=blend)


def apply_pencil(image: Image.Image, config: PencilConfig) -> Image.Image:
    """Apply a pencil-sketch effect by inverting a blurred grayscale layer."""
    if not config.enabled:
        return image

    original = image.convert("RGBA")
    grey = image.convert("L")
    inverted = grey.point(lambda p: 255 - p)
    blurred = inverted.filter(ImageFilter.GaussianBlur(radius=config.blur_radius))

    # Dodge blend: grey / (1 - blurred/255)
    grey_f = grey.convert("F")
    blur_f = blurred.convert("F")

    import PIL.ImageChops as IC
    import PIL.ImageMath as IM

    dodge = IM.eval(
        grey_f,
        blur_f,
        lambda g, b: (g * 255.0) / (255.0 - b + 1e-6),
    )
    sketch = dodge.convert("L")
    sketch_rgba = sketch.convert("RGBA")

    return Image.blend(original, sketch_rgba, config.blend)
