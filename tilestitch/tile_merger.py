"""Merge multiple tile dictionaries into a single flat mapping."""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

TileKey = Tuple[int, int, int]  # (z, x, y)
TileData = bytes
TileMap = Dict[TileKey, TileData]


class TileMergeError(Exception):
    """Raised when tile maps cannot be merged."""


def merge_tile_maps(
    maps: Iterable[TileMap],
    *,
    on_conflict: str = "first",
) -> TileMap:
    """Merge multiple tile maps into one.

    Parameters
    ----------
    maps:
        Iterable of tile maps to merge.
    on_conflict:
        Strategy when the same key appears in more than one map.
        ``"first"`` keeps the first value seen (default).
        ``"last"`` keeps the last value seen.
        ``"error"`` raises :class:`TileMergeError`.
    """
    if on_conflict not in {"first", "last", "error"}:
        raise ValueError(f"Unknown on_conflict strategy: {on_conflict!r}")

    result: TileMap = {}
    for tile_map in maps:
        for key, data in tile_map.items():
            if key in result:
                if on_conflict == "error":
                    raise TileMergeError(f"Duplicate tile key: {key}")
                if on_conflict == "last":
                    result[key] = data
                # "first" → do nothing
            else:
                result[key] = data
    return result


def tile_map_stats(tile_map: TileMap) -> dict:
    """Return basic statistics about a tile map."""
    if not tile_map:
        return {"count": 0, "total_bytes": 0, "zoom_levels": []}
    zooms = sorted({z for z, _x, _y in tile_map})
    total = sum(len(v) for v in tile_map.values())
    return {"count": len(tile_map), "total_bytes": total, "zoom_levels": zooms}
