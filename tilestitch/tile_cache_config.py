"""Configuration for tile caching behaviour."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

_DEFAULT_CACHE_DIR = Path.home() / ".tilestitch" / "cache"
_DEFAULT_MAX_SIZE_MB = 512


@dataclass
class TileCacheConfig:
    enabled: bool = True
    cache_dir: Path = field(default_factory=lambda: _DEFAULT_CACHE_DIR)
    max_size_mb: int = _DEFAULT_MAX_SIZE_MB

    def __post_init__(self) -> None:
        if isinstance(self.cache_dir, str):
            self.cache_dir = Path(self.cache_dir)
        if self.max_size_mb <= 0:
            raise ValueError("max_size_mb must be a positive integer")

    @property
    def max_size_bytes(self) -> int:
        return self.max_size_mb * 1024 * 1024


def tile_cache_config_from_env() -> TileCacheConfig:
    """Build a TileCacheConfig from environment variables."""
    enabled = os.environ.get("TILESTITCH_CACHE_ENABLED", "true").strip().lower() != "false"
    cache_dir = Path(os.environ.get("TILESTITCH_CACHE_DIR", str(_DEFAULT_CACHE_DIR)))
    try:
        max_size_mb = int(os.environ.get("TILESTITCH_CACHE_MAX_SIZE_MB", str(_DEFAULT_MAX_SIZE_MB)))
    except ValueError:
        max_size_mb = _DEFAULT_MAX_SIZE_MB
    return TileCacheConfig(enabled=enabled, cache_dir=cache_dir, max_size_mb=max_size_mb)
