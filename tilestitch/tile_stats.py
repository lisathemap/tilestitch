"""Tile fetch statistics aggregation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Tuple

TileKey = Tuple[int, int, int]  # (x, y, zoom)


@dataclass
class TileStats:
    total: int = 0
    fetched: int = 0
    cached: int = 0
    failed: int = 0
    skipped: int = 0
    bytes_downloaded: int = 0
    _per_zoom: Dict[int, int] = field(default_factory=dict, repr=False)

    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.fetched + self.cached) / self.total

    @property
    def per_zoom(self) -> Dict[int, int]:
        return dict(self._per_zoom)

    def record_fetched(self, key: TileKey, size_bytes: int = 0) -> None:
        self.fetched += 1
        self.total += 1
        self.bytes_downloaded += size_bytes
        self._per_zoom[key[2]] = self._per_zoom.get(key[2], 0) + 1

    def record_cached(self, key: TileKey) -> None:
        self.cached += 1
        self.total += 1
        self._per_zoom[key[2]] = self._per_zoom.get(key[2], 0) + 1

    def record_failed(self, key: TileKey) -> None:
        self.failed += 1
        self.total += 1

    def record_skipped(self, key: TileKey) -> None:
        self.skipped += 1
        self.total += 1

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "fetched": self.fetched,
            "cached": self.cached,
            "failed": self.failed,
            "skipped": self.skipped,
            "bytes_downloaded": self.bytes_downloaded,
            "success_rate": round(self.success_rate, 4),
            "per_zoom": self.per_zoom,
        }


def merge_stats(stats: Iterable[TileStats]) -> TileStats:
    """Combine multiple TileStats into one."""
    result = TileStats()
    for s in stats:
        result.total += s.total
        result.fetched += s.fetched
        result.cached += s.cached
        result.failed += s.failed
        result.skipped += s.skipped
        result.bytes_downloaded += s.bytes_downloaded
        for zoom, count in s._per_zoom.items():
            result._per_zoom[zoom] = result._per_zoom.get(zoom, 0) + count
    return result
