"""Input validation utilities for tilestitch."""

from typing import Tuple

BBox = Tuple[float, float, float, float]

MIN_ZOOM = 0
MAX_ZOOM = 19
MIN_LAT = -85.051129
MAX_LAT = 85.051129
MIN_LON = -180.0
MAX_LON = 180.0


class ValidationError(ValueError):
    """Raised when user-supplied inputs fail validation."""


def validate_zoom(zoom: int) -> int:
    """Validate that zoom is an integer in [0, 19].

    Args:
        zoom: Tile zoom level.

    Returns:
        The validated zoom level.

    Raises:
        ValidationError: If zoom is out of range or not an integer.
    """
    if not isinstance(zoom, int):
        raise ValidationError(f"Zoom must be an integer, got {type(zoom).__name__}.")
    if not (MIN_ZOOM <= zoom <= MAX_ZOOM):
        raise ValidationError(
            f"Zoom must be between {MIN_ZOOM} and {MAX_ZOOM}, got {zoom}."
        )
    return zoom


def validate_bbox(bbox: BBox) -> BBox:
    """Validate a bounding box (min_lon, min_lat, max_lon, max_lat).

    Args:
        bbox: Tuple of (min_lon, min_lat, max_lon, max_lat).

    Returns:
        The validated bounding box.

    Raises:
        ValidationError: If any value is out of range or the box is degenerate.
    """
    if len(bbox) != 4:
        raise ValidationError(f"BBox must have exactly 4 values, got {len(bbox)}.")

    min_lon, min_lat, max_lon, max_lat = bbox

    for lat in (min_lat, max_lat):
        if not (MIN_LAT <= lat <= MAX_LAT):
            raise ValidationError(
                f"Latitude {lat} out of range [{MIN_LAT}, {MAX_LAT}]."
            )

    for lon in (min_lon, max_lon):
        if not (MIN_LON <= lon <= MAX_LON):
            raise ValidationError(
                f"Longitude {lon} out of range [{MIN_LON}, {MAX_LON}]."
            )

    if min_lat >= max_lat:
        raise ValidationError(
            f"min_lat ({min_lat}) must be less than max_lat ({max_lat})."
        )

    if min_lon >= max_lon:
        raise ValidationError(
            f"min_lon ({min_lon}) must be less than max_lon ({max_lon})."
        )

    return bbox
