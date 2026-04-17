"""Crop a stitched image to the exact bounding box requested."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from PIL import Image

from tilestitch.tile_math import TileBounds, tile_to_lat_lon


class CropError(Exception):
    """Raised when cropping fails."""


@dataclass(frozen=True)
class CropBox:
    left: int
    upper: int
    right: int
    lower: int

    def as_tuple(self) -> Tuple[int, int, int, int]:
        return (self.left, self.upper, self.right, self.lower)


def compute_crop_box(
    bbox: Tuple[float, float, float, float],
    bounds: TileBounds,
    tile_size: int = 256,
) -> CropBox:
    """Return pixel offsets to crop the stitched canvas to *bbox*.

    Args:
        bbox: (min_lon, min_lat, max_lon, max_lat) in degrees.
        bounds: TileBounds describing the tile grid that was stitched.
        tile_size: Pixel size of a single tile.
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    zoom = bounds.zoom

    origin_lat, origin_lon = tile_to_lat_lon(bounds.x_min, bounds.y_min, zoom)
    end_lat, end_lon = tile_to_lat_lon(bounds.x_max + 1, bounds.y_max + 1, zoom)

    total_lon = end_lon - origin_lon
    total_lat = origin_lat - end_lat  # lat decreases downward

    canvas_w = (bounds.x_max - bounds.x_min + 1) * tile_size
    canvas_h = (bounds.y_max - bounds.y_min + 1) * tile_size

    if total_lon == 0 or total_lat == 0:
        raise CropError("Degenerate tile bounds: zero span.")

    left = int((min_lon - origin_lon) / total_lon * canvas_w)
    right = int((max_lon - origin_lon) / total_lon * canvas_w)
    upper = int((origin_lat - max_lat) / total_lat * canvas_h)
    lower = int((origin_lat - min_lat) / total_lat * canvas_h)

    left = max(0, min(left, canvas_w))
    right = max(0, min(right, canvas_w))
    upper = max(0, min(upper, canvas_h))
    lower = max(0, min(lower, canvas_h))

    if right <= left or lower <= upper:
        raise CropError("Computed crop box has zero or negative area.")

    return CropBox(left=left, upper=upper, right=right, lower=lower)


def crop_image(
    image: Image.Image,
    bbox: Tuple[float, float, float, float],
    bounds: TileBounds,
    tile_size: int = 256,
) -> Image.Image:
    """Crop *image* to the geographic *bbox*."""
    box = compute_crop_box(bbox, bounds, tile_size)
    return image.crop(box.as_tuple())
