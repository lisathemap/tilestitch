"""Simple disk-based tile cache for tilestitch."""

import hashlib
import os
from pathlib import Path
from typing import Optional

DEFAULT_CACHE_DIR = Path.home() / ".tilestitch" / "cache"


def _tile_cache_path(cache_dir: Path, url: str) -> Path:
    """Return the file path for a cached tile given its URL."""
    key = hashlib.sha256(url.encode()).hexdigest()
    return cache_dir / key[:2] / key[2:4] / key


def get_cached_tile(url: str, cache_dir: Optional[Path] = None) -> Optional[bytes]:
    """Return cached tile bytes for *url*, or None if not cached."""
    cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
    path = _tile_cache_path(cache_dir, url)
    if path.exists():
        return path.read_bytes()
    return None


def store_tile(url: str, data: bytes, cache_dir: Optional[Path] = None) -> Path:
    """Persist *data* for *url* in the cache and return the file path."""
    cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
    path = _tile_cache_path(cache_dir, url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def clear_cache(cache_dir: Optional[Path] = None) -> int:
    """Delete all cached tiles.  Returns the number of files removed."""
    cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
    removed = 0
    if cache_dir.exists():
        for file in cache_dir.rglob("*"):
            if file.is_file():
                file.unlink()
                removed += 1
    return removed


def cache_size(cache_dir: Optional[Path] = None) -> int:
    """Return total size in bytes of all cached tiles."""
    cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
    if not cache_dir.exists():
        return 0
    return sum(f.stat().st_size for f in cache_dir.rglob("*") if f.is_file())
