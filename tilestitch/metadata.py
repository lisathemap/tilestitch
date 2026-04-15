"""Metadata generation for stitched tile images."""

from dataclasses import dataclass, asdict
from typing import Tuple
import json

from tilestitch.tile_math import TileBounds


@dataclass
class ImageMetadata:
    """Metadata describing a stitched tile image."""

    source: str
    zoom: int
    bbox: Tuple[float, float, float, float]  # (min_lat, min_lon, max_lat, max_lon)
    tile_bounds: Tuple[int, int, int, int]   # (x_min, y_min, x_max, y_max)
    image_width: int
    image_height: int
    tile_count: int
    crs: str = "EPSG:4326"

    def to_dict(self) -> dict:
        """Return metadata as a plain dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize metadata to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


def build_metadata(
    source: str,
    zoom: int,
    bbox: Tuple[float, float, float, float],
    bounds: TileBounds,
    image_width: int,
    image_height: int,
) -> ImageMetadata:
    """Construct an ImageMetadata instance from pipeline parameters.

    Args:
        source: Name of the tile source used.
        zoom: Zoom level of the tiles.
        bbox: Bounding box as (min_lat, min_lon, max_lat, max_lon).
        bounds: TileBounds namedtuple from tile_math.
        image_width: Width of the stitched image in pixels.
        image_height: Height of the stitched image in pixels.

    Returns:
        Populated ImageMetadata instance.
    """
    tile_count = (bounds.x_max - bounds.x_min + 1) * (bounds.y_max - bounds.y_min + 1)
    return ImageMetadata(
        source=source,
        zoom=zoom,
        bbox=bbox,
        tile_bounds=(bounds.x_min, bounds.y_min, bounds.x_max, bounds.y_max),
        image_width=image_width,
        image_height=image_height,
        tile_count=tile_count,
    )


def save_metadata(metadata: ImageMetadata, path: str) -> None:
    """Write metadata as JSON to the given file path."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(metadata.to_json())
