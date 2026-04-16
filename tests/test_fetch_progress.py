"""Tests for tilestitch.fetch_progress."""

from __future__ import annotations

import io
from unittest.mock import patch

import pytest

from tilestitch.tile_math import TileBounds
from tilestitch.fetch_progress import bounds_to_keys, fetch_with_progress


# ---------------------------------------------------------------------------
# bounds_to_keys
# ---------------------------------------------------------------------------

class TestBoundsToKeys:
    def _bounds(self, z=2, x_min=1, x_max=2, y_min=3, y_max=4) -> TileBounds:
        return TileBounds(zoom=z, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)

    def test_count_matches_grid(self):
        b = self._bounds(x_min=0, x_max=1, y_min=0, y_max=1)
        keys = bounds_to_keys(b)
        assert len(keys) == 4

    def test_single_tile(self):
        b = self._bounds(x_min=5, x_max=5, y_min=7, y_max=7)
        keys = bounds_to_keys(b)
        assert keys == [(2, 5, 7)]

    def test_zoom_preserved(self):
        b = self._bounds(z=10, x_min=0, x_max=0, y_min=0, y_max=0)
        keys = bounds_to_keys(b)
        assert keys[0][0] == 10

    def test_all_keys_are_tuples_of_three(self):
        b = self._bounds(x_min=0, x_max=2, y_min=0, y_max=2)
        for key in bounds_to_keys(b):
            assert len(key) == 3


# ---------------------------------------------------------------------------
# fetch_with_progress
# ---------------------------------------------------------------------------

FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8


def _fake_fetch_tiles(urls, concurrency=8):
    """Return fake PNG bytes for every URL."""
    return [FAKE_PNG for _ in urls]


def _failing_fetch_tiles(urls, concurrency=8):
    """Return None for every URL (simulate all failures)."""
    return [None for _ in urls]


class TestFetchWithProgress:
    def _buf(self):
        return io.StringIO()

    @patch("tilestitch.fetch_progress.fetch_tiles", side_effect=_fake_fetch_tiles)
    def test_returns_dict(self, _mock):
        buf = self._buf()
        result = fetch_with_progress(
            [(10, 0, 0)], "https://t/{z}/{x}/{y}.png", stream=buf
        )
        assert isinstance(result, dict)

    @patch("tilestitch.fetch_progress.fetch_tiles", side_effect=_fake_fetch_tiles)
    def test_successful_tiles_in_result(self, _mock):
        buf = self._buf()
        keys = [(10, 0, 0), (10, 1, 0)]
        result = fetch_with_progress(keys, "https://t/{z}/{x}/{y}.png", stream=buf)
        assert set(result.keys()) == {(10, 0, 0), (10, 1, 0)}

    @patch("tilestitch.fetch_progress.fetch_tiles", side_effect=_failing_fetch_tiles)
    def test_failed_tiles_excluded(self, _mock):
        buf = self._buf()
        result = fetch_with_progress(
            [(10, 0, 0)], "https://t/{z}/{x}/{y}.png", stream=buf
        )
        assert result == {}

    @patch("tilestitch.fetch_progress.fetch_tiles", side_effect=_fake_fetch_tiles)
    def test_progress_written_to_stream(self, _mock):
        buf = self._buf()
        fetch_with_progress([(10, 0, 0)], "https://t/{z}/{x}/{y}.png", stream=buf)
        assert len(buf.getvalue()) > 0

    @patch("tilestitch.fetch_progress.fetch_tiles", side_effect=_fake_fetch_tiles)
    def test_empty_keys_returns_empty_dict(self, _mock):
        buf = self._buf()
        result = fetch_with_progress([], "https://t/{z}/{x}/{y}.png", stream=buf)
        assert result == {}

    @patch("tilestitch.fetch_progress.fetch_tiles", side_effect=_fake_fetch_tiles)
    def test_tile_data_matches_fake_png(self, _mock):
        buf = self._buf()
        result = fetch_with_progress(
            [(5, 3, 3)], "https://t/{z}/{x}/{y}.png", stream=buf
        )
        assert result[(5, 3, 3)] == FAKE_PNG
