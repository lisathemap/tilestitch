"""Utilities for parsing and normalising bounding-box strings."""

from __future__ import annotations

from typing import Tuple

BBox = Tuple[float, float, float, float]  # (min_lon, min_lat, max_lon, max_lat)


class BBoxParseError(ValueError):
    """Raised when a bounding-box string cannot be parsed or is invalid."""


def parse_bbox(raw: str) -> BBox:
    """Parse a comma-separated bounding-box string into a (min_lon, min_lat, max_lon, max_lat) tuple.

    Args:
        raw: A string in the form ``"min_lon,min_lat,max_lon,max_lat"``.

    Returns:
        A 4-tuple of floats.

    Raises:
        BBoxParseError: If the string cannot be split into exactly four numeric
            values or the coordinate ranges are invalid.
    """
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 4:
        raise BBoxParseError(
            f"Expected 4 comma-separated values, got {len(parts)}: {raw!r}"
        )

    try:
        min_lon, min_lat, max_lon, max_lat = (float(p) for p in parts)
    except ValueError as exc:
        raise BBoxParseError(f"Non-numeric value in bbox string {raw!r}") from exc

    _validate_bbox_values(min_lon, min_lat, max_lon, max_lat)
    return min_lon, min_lat, max_lon, max_lat


def _validate_bbox_values(
    min_lon: float, min_lat: float, max_lon: float, max_lat: float
) -> None:
    """Raise *BBoxParseError* if any coordinate value is out of range."""
    if not (-180.0 <= min_lon <= 180.0) or not (-180.0 <= max_lon <= 180.0):
        raise BBoxParseError(
            f"Longitude values must be in [-180, 180], got {min_lon}, {max_lon}"
        )
    if not (-90.0 <= min_lat <= 90.0) or not (-90.0 <= max_lat <= 90.0):
        raise BBoxParseError(
            f"Latitude values must be in [-90, 90], got {min_lat}, {max_lat}"
        )
    if min_lon >= max_lon:
        raise BBoxParseError(
            f"min_lon ({min_lon}) must be less than max_lon ({max_lon})"
        )
    if min_lat >= max_lat:
        raise BBoxParseError(
            f"min_lat ({min_lat}) must be less than max_lat ({max_lat})"
        )


def bbox_to_str(bbox: BBox) -> str:
    """Format a BBox tuple back into a canonical comma-separated string."""
    return ",".join(str(v) for v in bbox)
