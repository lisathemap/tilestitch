"""Filtering utilities for tile collections."""

from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Tuple

from tilestitch.tile_math import TileBounds

# A tile key is (x, y, z)
TileKey = Tuple[int, int, int]
TileData = Dict[TileKey, bytes]


class TileFilterError(Exception):
    """Raised when a filter cannot be applied."""


def filter_tiles(
    tiles: TileData,
    predicate: Callable[[TileKey, bytes], bool],
) -> TileData:
    """Return a new dict containing only tiles for which *predicate* is True."""
    return {key: data for key, data in tiles.items() if predicate(key, data)}


def drop_empty_tiles(tiles: TileData, empty_threshold: int = 64) -> TileData:
    """Drop tiles whose payload is suspiciously small (likely blank/error tiles).

    Args:
        tiles: Mapping of tile key -> raw bytes.
        empty_threshold: Tiles with fewer bytes than this are considered empty.

    Returns:
        Filtered tile mapping.
    """
    if empty_threshold < 0:
        raise TileFilterError("empty_threshold must be >= 0")
    return filter_tiles(tiles, lambda _key, data: len(data) >= empty_threshold)


def keep_within_bounds(tiles: TileData, bounds: TileBounds) -> TileData:
    """Return only tiles whose (x, y, z) coordinates fall inside *bounds*.

    Args:
        tiles: Mapping of tile key -> raw bytes.
        bounds: A TileBounds namedtuple (x_min, x_max, y_min, y_max, zoom).

    Returns:
        Filtered tile mapping.
    """

    def _within(key: TileKey, _data: bytes) -> bool:
        x, y, z = key
        return (
            z == bounds.zoom
            and bounds.x_min <= x <= bounds.x_max
            and bounds.y_min <= y <= bounds.y_max
        )

    return filter_tiles(tiles, _within)


def tile_keys_from_bounds(bounds: TileBounds) -> List[TileKey]:
    """Enumerate all (x, y, z) keys covered by *bounds*."""
    return [
        (x, y, bounds.zoom)
        for x in range(bounds.x_min, bounds.x_max + 1)
        for y in range(bounds.y_min, bounds.y_max + 1)
    ]


def missing_keys(tiles: TileData, bounds: TileBounds) -> List[TileKey]:
    """Return tile keys expected from *bounds* that are absent in *tiles*."""
    expected = set(tile_keys_from_bounds(bounds))
    present = set(tiles.keys())
    return sorted(expected - present)
