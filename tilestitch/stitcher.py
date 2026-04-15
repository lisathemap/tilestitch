"""Tile stitching: combine fetched tiles into a single PIL image."""

from __future__ import annotations

from io import BytesIO
from typing import Dict, List, Tuple

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise ImportError("Pillow is required for stitching: pip install Pillow") from exc

from tilestitch.tile_math import TileBounds


def _tile_size() -> int:
    """Standard OSM-style tile size in pixels."""
    return 256


def stitch_tiles(
    tile_data: Dict[Tuple[int, int], bytes],
    bounds: TileBounds,
) -> Image.Image:
    """Stitch a mapping of (tx, ty) -> raw PNG bytes into one image.

    Parameters
    ----------
    tile_data:
        Dictionary keyed by ``(tile_x, tile_y)`` containing raw image bytes.
    bounds:
        :class:`~tilestitch.tile_math.TileBounds` describing the grid extent.

    Returns
    -------
    PIL.Image.Image
        Single RGBA image composed of all tiles.
    """
    tile_px = _tile_size()
    cols = bounds.max_x - bounds.min_x + 1
    rows = bounds.max_y - bounds.min_y + 1

    canvas = Image.new("RGBA", (cols * tile_px, rows * tile_px))

    for (tx, ty), raw in tile_data.items():
        col = tx - bounds.min_x
        row = ty - bounds.min_y
        try:
            tile_img = Image.open(BytesIO(raw)).convert("RGBA")
        except Exception:
            tile_img = Image.new("RGBA", (tile_px, tile_px), (200, 200, 200, 255))
        canvas.paste(tile_img, (col * tile_px, row * tile_px))

    return canvas


def save_image(image: Image.Image, path: str, fmt: str = "PNG") -> None:
    """Save *image* to *path* using the given format.

    Parameters
    ----------
    image:
        Composed PIL image.
    path:
        Destination file path.
    fmt:
        Image format understood by Pillow (default ``"PNG"``).  Use
        ``"JPEG"`` for smaller files when transparency is not needed.
    """
    image.save(path, format=fmt)
