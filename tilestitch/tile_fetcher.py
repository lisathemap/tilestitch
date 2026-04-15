"""Fetch map tiles from remote tile servers, with optional disk caching."""

import logging
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from tilestitch.cache import get_cached_tile, store_tile
from tilestitch.tile_math import TileBounds

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = "tilestitch/1.0 (+https://github.com/tilestitch/tilestitch)"
DEFAULT_TIMEOUT = 10  # seconds


def _build_session(user_agent: str = DEFAULT_USER_AGENT) -> requests.Session:
    """Return a requests Session with retry logic and a custom User-Agent."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": user_agent})
    return session


def fetch_tile(
    url: str,
    session: Optional[requests.Session] = None,
    cache_dir: Optional[Path] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> bytes:
    """Fetch a single tile by *url*, using the disk cache when available."""
    cached = get_cached_tile(url, cache_dir=cache_dir)
    if cached is not None:
        logger.debug("Cache hit: %s", url)
        return cached

    session = session or _build_session()
    logger.debug("Fetching: %s", url)
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    data = response.content
    store_tile(url, data, cache_dir=cache_dir)
    return data


def fetch_tiles(
    url_map: Dict[Tuple[int, int], str],
    session: Optional[requests.Session] = None,
    cache_dir: Optional[Path] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[Tuple[int, int], bytes]:
    """Fetch multiple tiles given a mapping of (x, y) -> url.

    Returns a dict of (x, y) -> raw PNG bytes.
    Missing or failed tiles are logged and omitted from the result.
    """
    session = session or _build_session()
    results: Dict[Tuple[int, int], bytes] = {}
    for (x, y), url in url_map.items():
        try:
            results[(x, y)] = fetch_tile(url, session=session, cache_dir=cache_dir, timeout=timeout)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to fetch tile (%d, %d) from %s: %s", x, y, url, exc)
    return results
