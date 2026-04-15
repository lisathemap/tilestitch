"""Fetch map tiles from a tile server URL template."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from tilestitch.tile_math import TileBounds

logger = logging.getLogger(__name__)

TileCoord = Tuple[int, int, int]  # (x, y, zoom)
TileCache = Dict[TileCoord, bytes]

DEFAULT_USER_AGENT = "tilestitch/0.1 (https://github.com/youruser/tilestitch)"
DEFAULT_TIMEOUT = 10
DEFAULT_MAX_RETRIES = 3


def _build_session(max_retries: int = DEFAULT_MAX_RETRIES) -> requests.Session:
    """Create a requests session with retry logic."""
    session = requests.Session()
    retry = Retry(
        total=max_retries,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": DEFAULT_USER_AGENT})
    return session


def fetch_tile(
    url_template: str,
    x: int,
    y: int,
    zoom: int,
    session: Optional[requests.Session] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> bytes:
    """Fetch a single tile and return its raw bytes.

    Args:
        url_template: URL with {x}, {y}, {z} placeholders.
        x: Tile X coordinate.
        y: Tile Y coordinate.
        zoom: Zoom level.
        session: Optional requests session to reuse.
        timeout: Request timeout in seconds.

    Returns:
        Raw image bytes for the tile.

    Raises:
        requests.HTTPError: On non-2xx response.
    """
    url = url_template.format(x=x, y=y, z=zoom)
    sess = session or requests.Session()
    response = sess.get(url, timeout=timeout)
    response.raise_for_status()
    logger.debug("Fetched tile z=%d x=%d y=%d from %s", zoom, x, y, url)
    return response.content


def fetch_tiles(
    url_template: str,
    bounds: TileBounds,
    max_workers: int = 8,
    timeout: int = DEFAULT_TIMEOUT,
) -> TileCache:
    """Fetch all tiles within a TileBounds concurrently.

    Args:
        url_template: URL with {x}, {y}, {z} placeholders.
        bounds: TileBounds describing the tile grid to fetch.
        max_workers: Number of concurrent download threads.
        timeout: Per-request timeout in seconds.

    Returns:
        Dict mapping (x, y, zoom) to raw image bytes.
    """
    session = _build_session()
    results: TileCache = {}

    coords = [
        (x, y, bounds.zoom)
        for y in range(bounds.y_min, bounds.y_max + 1)
        for x in range(bounds.x_min, bounds.x_max + 1)
    ]

    logger.info("Fetching %d tiles at zoom %d", len(coords), bounds.zoom)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_coord = {
            executor.submit(fetch_tile, url_template, x, y, zoom, session, timeout): (x, y, zoom)
            for x, y, zoom in coords
        }
        for future in as_completed(future_to_coord):
            coord = future_to_coord[future]
            try:
                results[coord] = future.result()
            except Exception as exc:
                logger.error("Failed to fetch tile %s: %s", coord, exc)

    return results
