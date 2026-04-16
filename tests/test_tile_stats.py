"""Tests for tilestitch.tile_stats."""
import pytest
from tilestitch.tile_stats import TileStats, merge_stats

KEY_Z10 = (512, 340, 10)
KEY_Z11 = (1024, 680, 11)


class TestTileStatsDefaults:
    def test_all_zeros(self):
        s = TileStats()
        assert s.total == 0
        assert s.fetched == 0
        assert s.cached == 0
        assert s.failed == 0
        assert s.skipped == 0
        assert s.bytes_downloaded == 0

    def test_success_rate_zero_when_no_tiles(self):
        assert TileStats().success_rate == 0.0


class TestRecordFetched:
    def test_increments_total_and_fetched(self):
        s = TileStats()
        s.record_fetched(KEY_Z10, size_bytes=1024)
        assert s.total == 1
        assert s.fetched == 1

    def test_accumulates_bytes(self):
        s = TileStats()
        s.record_fetched(KEY_Z10, size_bytes=500)
        s.record_fetched(KEY_Z11, size_bytes=300)
        assert s.bytes_downloaded == 800

    def test_per_zoom_tracked(self):
        s = TileStats()
        s.record_fetched(KEY_Z10)
        s.record_fetched(KEY_Z10)
        assert s.per_zoom[10] == 2


class TestRecordCached:
    def test_increments_cached(self):
        s = TileStats()
        s.record_cached(KEY_Z10)
        assert s.cached == 1
        assert s.total == 1
        assert s.bytes_downloaded == 0


class TestRecordFailed:
    def test_increments_failed(self):
        s = TileStats()
        s.record_failed(KEY_Z10)
        assert s.failed == 1
        assert s.total == 1


class TestRecordSkipped:
    def test_increments_skipped(self):
        s = TileStats()
        s.record_skipped(KEY_Z10)
        assert s.skipped == 1
        assert s.total == 1


class TestSuccessRate:
    def test_all_fetched(self):
        s = TileStats()
        s.record_fetched(KEY_Z10)
        s.record_fetched(KEY_Z11)
        assert s.success_rate == 1.0

    def test_mixed(self):
        s = TileStats()
        s.record_fetched(KEY_Z10)
        s.record_failed(KEY_Z11)
        assert s.success_rate == pytest.approx(0.5)


class TestToDict:
    def test_contains_expected_keys(self):
        d = TileStats().to_dict()
        for key in ("total", "fetched", "cached", "failed", "skipped", "bytes_downloaded", "success_rate", "per_zoom"):
            assert key in d


class TestMergeStats:
    def test_empty_iterable(self):
        result = merge_stats([])
        assert result.total == 0

    def test_combines_totals(self):
        a, b = TileStats(), TileStats()
        a.record_fetched(KEY_Z10, 100)
        b.record_cached(KEY_Z11)
        merged = merge_stats([a, b])
        assert merged.total == 2
        assert merged.fetched == 1
        assert merged.cached == 1
        assert merged.bytes_downloaded == 100

    def test_per_zoom_merged(self):
        a, b = TileStats(), TileStats()
        a.record_fetched(KEY_Z10)
        b.record_fetched(KEY_Z10)
        merged = merge_stats([a, b])
        assert merged.per_zoom[10] == 2
