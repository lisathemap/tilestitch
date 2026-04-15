"""High-level pipeline: bbox → tiles → stitched image."""

from __future__ import annotations

from typing import Optional

from tilestitch.tile_math import tiles_for_bbox
from tilestitch.tile_fetcher import fetch_tiles
from tilestitch.sources import get_source, tile_url
from tilestitch.stitcher import stitch_tiles, save_image


def run(
    bbox: tuple[float, float, float, float],
    zoom: int,
    source_name: str = "osm",
    output_path: str = "output.png",
    fmt: str = "PNG",
    workers: int = 8,
    timeout: float = 10.0,
) -> str:
    """Fetch and stitch tiles for *bbox* at *zoom* and write to *output_path*.

    Parameters
    ----------
    bbox:
        ``(min_lon, min_lat, max_lon, max_lat)`` in WGS-84 degrees.
    zoom:
        Tile zoom level (0-19).
    source_name:
        Tile source identifier recognised by :func:`~tilestitch.sources.get_source`.
    output_path:
        Destination file path for the stitched image.
    fmt:
        Pillow format string, e.g. ``"PNG"`` or ``"JPEG"``.
    workers:
        Number of concurrent download threads.
    timeout:
        Per-request timeout in seconds.

    Returns
    -------
    str
        Absolute path to the written file.
    """
    min_lon, min_lat, max_lon, max_lat = bbox

    source = get_source(source_name)
    bounds = tiles_for_bbox(min_lat, min_lon, max_lat, max_lon, zoom)

    urls: dict[tuple[int, int], str] = {}
    for tx in range(bounds.min_x, bounds.max_x + 1):
        for ty in range(bounds.min_y, bounds.max_y + 1):
            urls[(tx, ty)] = tile_url(source, zoom, tx, ty)

    raw_tiles = fetch_tiles(
        list(urls.values()),
        workers=workers,
        timeout=timeout,
    )

    # Re-key raw_tiles (list of bytes, same order as urls.values()) by (tx, ty)
    keyed: dict[tuple[int, int], bytes] = {}
    for (coord, _url), data in zip(urls.items(), raw_tiles):
        if data is not None:
            keyed[coord] = data

    image = stitch_tiles(keyed, bounds)
    save_image(image, output_path, fmt=fmt)

    import os
    return os.path.abspath(output_path)
