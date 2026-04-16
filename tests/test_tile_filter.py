"""Tests for tilestitch.tile_filter."""

from __future__ import annotations

import pytest

from tilestitch.tile_math import TileBounds
from tilestitch.tile_filter import (
    TileFilterError,
    drop_empty_tiles,
    filter_tiles,
    keep_within_bounds,
    missing_keys,
    tile_keys_from_bounds,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bounds(x_min=0, x_max=1, y_min=0, y_max=1, zoom=5) -> TileBounds:
    return TileBounds(x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, zoom=zoom)


def _tiles():
    return {
        (0, 0, 5): b"x" * 100,
        (0, 1, 5): b"x" * 100,
        (1, 0, 5): b"x" * 100,
        (1, 1, 5): b"x" * 100,
    }


# ---------------------------------------------------------------------------
# filter_tiles
# ---------------------------------------------------------------------------

class TestFilterTiles:
    def test_keeps_matching(self):
        tiles = _tiles()
        result = filter_tiles(tiles, lambda key, _: key[0] == 0)
        assert all(k[0] == 0 for k in result)

    def test_drops_non_matching(self):
        tiles = _tiles()
        result = filter_tiles(tiles, lambda key, _: key[0] == 0)
        assert (1, 0, 5) not in result

    def test_empty_input_returns_empty(self):
        assert filter_tiles({}, lambda k, d: True) == {}


# ---------------------------------------------------------------------------
# drop_empty_tiles
# ---------------------------------------------------------------------------

class TestDropEmptyTiles:
    def test_removes_small_payloads(self):
        tiles = {(0, 0, 1): b"tiny", (1, 0, 1): b"x" * 200}
        result = drop_empty_tiles(tiles)
        assert (0, 0, 1) not in result
        assert (1, 0, 1) in result

    def test_keeps_tiles_at_threshold(self):
        tiles = {(0, 0, 1): b"x" * 64}
        result = drop_empty_tiles(tiles, empty_threshold=64)
        assert (0, 0, 1) in result

    def test_negative_threshold_raises(self):
        with pytest.raises(TileFilterError):
            drop_empty_tiles({}, empty_threshold=-1)

    def test_zero_threshold_keeps_all(self):
        tiles = {(0, 0, 1): b""}
        assert (0, 0, 1) in drop_empty_tiles(tiles, empty_threshold=0)


# ---------------------------------------------------------------------------
# keep_within_bounds
# ---------------------------------------------------------------------------

class TestKeepWithinBounds:
    def test_filters_out_of_bounds_tiles(self):
        tiles = _tiles()
        tiles[(5, 5, 5)] = b"x" * 100  # outside
        result = keep_within_bounds(tiles, _bounds())
        assert (5, 5, 5) not in result

    def test_keeps_tiles_inside_bounds(self):
        tiles = _tiles()
        result = keep_within_bounds(tiles, _bounds())
        assert len(result) == 4

    def test_wrong_zoom_excluded(self):
        tiles = {(0, 0, 9): b"x" * 100}
        result = keep_within_bounds(tiles, _bounds(zoom=5))
        assert result == {}


# ---------------------------------------------------------------------------
# tile_keys_from_bounds / missing_keys
# ---------------------------------------------------------------------------

class TestTileKeysFromBounds:
    def test_count_matches_grid(self):
        keys = tile_keys_from_bounds(_bounds(x_min=0, x_max=2, y_min=0, y_max=2))
        assert len(keys) == 9  # 3x3

    def test_zoom_preserved(self):
        keys = tile_keys_from_bounds(_bounds(zoom=7))
        assert all(z == 7 for _, _, z in keys)


class TestMissingKeys:
    def test_all_present_returns_empty(self):
        tiles = _tiles()
        assert missing_keys(tiles, _bounds()) == []

    def test_detects_missing_tile(self):
        tiles = _tiles()
        del tiles[(1, 1, 5)]
        assert (1, 1, 5) in missing_keys(tiles, _bounds())

    def test_extra_tiles_ignored(self):
        tiles = _tiles()
        tiles[(99, 99, 5)] = b"x" * 100
        assert missing_keys(tiles, _bounds()) == []
