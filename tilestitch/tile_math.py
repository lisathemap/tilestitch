"""Utility functions for tile coordinate math (slippy map / XYZ tiles)."""

import math
from dataclasses import dataclass


@dataclass
class TileBounds:
    """Bounding box of a tile or tile range in geographic coordinates."""
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float


def lat_lon_to_tile(lat: float, lon: float, zoom: int) -> tuple[int, int]:
    """Convert latitude/longitude to XYZ tile coordinates at a given zoom level."""
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {lon}")
    if not (0 <= zoom <= 22):
        raise ValueError(f"Zoom must be between 0 and 22, got {zoom}")

    lat_rad = math.radians(lat)
    n = 2 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    # Clamp to valid range
    x = max(0, min(n - 1, x))
    y = max(0, min(n - 1, y))
    return x, y


def tile_to_lat_lon(x: int, y: int, zoom: int) -> tuple[float, float]:
    """Convert XYZ tile coordinates to the lat/lon of the tile's NW corner."""
    n = 2 ** zoom
    lon = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat = math.degrees(lat_rad)
    return lat, lon


def tile_bounds(x: int, y: int, zoom: int) -> TileBounds:
    """Return the geographic bounding box of a tile."""
    nw_lat, nw_lon = tile_to_lat_lon(x, y, zoom)
    se_lat, se_lon = tile_to_lat_lon(x + 1, y + 1, zoom)
    return TileBounds(
        min_lon=nw_lon,
        min_lat=se_lat,
        max_lon=se_lon,
        max_lat=nw_lat,
    )


def tiles_for_bbox(
    min_lon: float, min_lat: float, max_lon: float, max_lat: float, zoom: int
) -> list[tuple[int, int]]:
    """Return all tile (x, y) pairs that cover the given bounding box at a zoom level."""
    x_min, y_max = lat_lon_to_tile(min_lat, min_lon, zoom)
    x_max, y_min = lat_lon_to_tile(max_lat, max_lon, zoom)
    return [
        (x, y)
        for x in range(x_min, x_max + 1)
        for y in range(y_min, y_max + 1)
    ]
