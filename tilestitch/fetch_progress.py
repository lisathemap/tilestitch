"""Wrapper that integrates ProgressTracker with tile fetching."""

from __future__ import annotations

import sys
from typing import Dict, Iterable, Optional, TextIO, Tuple

from tilestitch.progress import ProgressTracker
from tilestitch.tile_math import TileBounds
from tilestitch.tile_fetcher import fetch_tiles
from tilestitch.logger import get_logger

log = get_logger("fetch_progress")

TileKey = Tuple[int, int, int]   # (z, x, y)
TileMap = Dict[TileKey, bytes]


def fetch_with_progress(
    keys: Iterable[TileKey],
    url_template: str,
    *,
    stream: Optional[TextIO] = None,
    label: str = "Fetching tiles",
    concurrency: int = 8,
) -> TileMap:
    """Fetch *keys* using *url_template*, reporting live progress.

    Returns a mapping of ``(z, x, y)`` → raw PNG bytes for every tile that
    was retrieved successfully.  Failed tiles are counted but omitted.
    """
    key_list = list(keys)
    tracker = ProgressTracker(
        total=len(key_list),
        label=label,
        stream=stream if stream is not None else sys.stderr,
    )

    urls = [
        url_template.format(z=z, x=x, y=y)
        for z, x, y in key_list
    ]

    results: TileMap = {}
    raw = fetch_tiles(urls, concurrency=concurrency)

    for key, data in zip(key_list, raw):
        if data is None:
            log.warning("tile %s failed to fetch", key)
            tracker.advance(failed=True)
        else:
            results[key] = data
            tracker.advance()

    tracker.finish()
    return results


def bounds_to_keys(bounds: TileBounds) -> list[TileKey]:
    """Expand a :class:`TileBounds` into a flat list of (z, x, y) keys."""
    z = bounds.zoom
    return [
        (z, x, y)
        for x in range(bounds.x_min, bounds.x_max + 1)
        for y in range(bounds.y_min, bounds.y_max + 1)
    ]
