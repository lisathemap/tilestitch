"""Composite multiple stitched images into a single output image."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from PIL import Image


class CompositorError(Exception):
    """Raised when compositing fails."""


@dataclass
class CompositeLayer:
    image: Image.Image
    offset: Tuple[int, int]  # (x, y) pixel offset
    opacity: float = 1.0  # 0.0 – 1.0

    def __post_init__(self) -> None:
        if not (0.0 <= self.opacity <= 1.0):
            raise CompositorError(f"opacity must be between 0 and 1, got {self.opacity}")


def composite_layers(layers: List[CompositeLayer], size: Tuple[int, int]) -> Image.Image:
    """Composite a list of layers onto a blank canvas of *size* (width, height)."""
    if not layers:
        raise CompositorError("at least one layer is required")
    if size[0] <= 0 or size[1] <= 0:
        raise CompositorError(f"invalid canvas size: {size}")

    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    for layer in layers:
        img = layer.image.convert("RGBA")
        if layer.opacity < 1.0:
            r, g, b, a = img.split()
            a = a.point(lambda v: int(v * layer.opacity))
            img = Image.merge("RGBA", (r, g, b, a))
        canvas.paste(img, layer.offset, mask=img)
    return canvas


def auto_size(layers: List[CompositeLayer]) -> Tuple[int, int]:
    """Compute the bounding box that contains all layers."""
    if not layers:
        raise CompositorError("no layers provided")
    max_x = max(l.offset[0] + l.image.width for l in layers)
    max_y = max(l.offset[1] + l.image.height for l in layers)
    return (max_x, max_y)
