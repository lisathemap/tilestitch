"""High-level cache management using TileCacheConfig."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from tilestitch.tile_cache_config import TileCacheConfig
from tilestitch import cache as _cache


class CacheManager:
    """Wraps low-level cache operations with config-aware behaviour."""

    def __init__(self, config: TileCacheConfig) -> None:
        self._config = config

    @property
    def config(self) -> TileCacheConfig:
        return self._config

    def get(self, url: str) -> Optional[bytes]:
        """Return cached bytes for *url*, or None if disabled / missing."""
        if not self._config.enabled:
            return None
        return _cache.get_cached_tile(url, cache_dir=self._config.cache_dir)

    def store(self, url: str, data: bytes) -> None:
        """Persist *data* for *url* when caching is enabled."""
        if not self._config.enabled:
            return
        if self._would_exceed_limit(len(data)):
            return
        _cache.store_tile(url, data, cache_dir=self._config.cache_dir)

    def clear(self) -> None:
        """Remove all cached tiles."""
        _cache.clear_cache(cache_dir=self._config.cache_dir)

    def size(self) -> int:
        """Return total cache size in bytes."""
        return _cache.cache_size(cache_dir=self._config.cache_dir)

    def _would_exceed_limit(self, incoming: int) -> bool:
        return (self.size() + incoming) > self._config.max_size_bytes
