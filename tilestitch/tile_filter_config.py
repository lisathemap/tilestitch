"""Configuration dataclass for tile filtering behaviour."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


_DEFAULT_EMPTY_THRESHOLD = 64
_DEFAULT_DROP_EMPTY = True


@dataclass(frozen=True)
class TileFilterConfig:
    """Controls how fetched tiles are post-processed before stitching.

    Attributes:
        drop_empty: When True, tiles smaller than *empty_threshold* bytes are
            discarded before the image is assembled.
        empty_threshold: Minimum byte-length for a tile to be considered valid.
        enforce_bounds: When True, tiles outside the requested bounding box are
            removed even if they were returned by the fetcher.
    """

    drop_empty: bool = _DEFAULT_DROP_EMPTY
    empty_threshold: int = _DEFAULT_EMPTY_THRESHOLD
    enforce_bounds: bool = True

    def __post_init__(self) -> None:
        if self.empty_threshold < 0:
            raise ValueError("empty_threshold must be >= 0")


def tile_filter_config_from_env() -> TileFilterConfig:
    """Build a :class:`TileFilterConfig` from environment variables.

    Recognised variables:
        TILESTITCH_DROP_EMPTY   – "1"/"true" or "0"/"false" (default: true)
        TILESTITCH_EMPTY_BYTES  – integer byte threshold (default: 64)
        TILESTITCH_ENFORCE_BOUNDS – "1"/"true" or "0"/"false" (default: true)
    """

    def _bool(name: str, default: bool) -> bool:
        raw = os.environ.get(name, "").strip().lower()
        if raw in ("1", "true", "yes"):
            return True
        if raw in ("0", "false", "no"):
            return False
        return default

    def _int(name: str, default: int) -> int:
        raw = os.environ.get(name, "").strip()
        try:
            return int(raw) if raw else default
        except ValueError:
            return default

    return TileFilterConfig(
        drop_empty=_bool("TILESTITCH_DROP_EMPTY", _DEFAULT_DROP_EMPTY),
        empty_threshold=_int("TILESTITCH_EMPTY_BYTES", _DEFAULT_EMPTY_THRESHOLD),
        enforce_bounds=_bool("TILESTITCH_ENFORCE_BOUNDS", True),
    )
