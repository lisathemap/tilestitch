"""Tests for tilestitch.tile_merger."""

import pytest

from tilestitch.tile_merger import (
    TileMergeError,
    merge_tile_maps,
    tile_map_stats,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _map(*keys):
    """Build a TileMap where each key maps to its repr as bytes."""
    return {k: repr(k).encode() for k in keys}


A = (10, 1, 2)
B = (10, 3, 4)
C = (10, 5, 6)


# ---------------------------------------------------------------------------
# merge_tile_maps
# ---------------------------------------------------------------------------

class TestMergeTileMaps:
    def test_empty_iterable_returns_empty(self):
        assert merge_tile_maps([]) == {}

    def test_single_map_returned_as_is(self):
        m = _map(A, B)
        assert merge_tile_maps([m]) == m

    def test_two_disjoint_maps_combined(self):
        result = merge_tile_maps([_map(A), _map(B)])
        assert set(result) == {A, B}

    def test_three_maps_combined(self):
        result = merge_tile_maps([_map(A), _map(B), _map(C)])
        assert len(result) == 3

    def test_conflict_first_keeps_first(self):
        m1 = {A: b"first"}
        m2 = {A: b"second"}
        result = merge_tile_maps([m1, m2], on_conflict="first")
        assert result[A] == b"first"

    def test_conflict_last_keeps_last(self):
        m1 = {A: b"first"}
        m2 = {A: b"second"}
        result = merge_tile_maps([m1, m2], on_conflict="last")
        assert result[A] == b"second"

    def test_conflict_error_raises(self):
        m1 = {A: b"first"}
        m2 = {A: b"second"}
        with pytest.raises(TileMergeError):
            merge_tile_maps([m1, m2], on_conflict="error")

    def test_unknown_strategy_raises_value_error(self):
        with pytest.raises(ValueError):
            merge_tile_maps([_map(A)], on_conflict="unknown")

    def test_no_conflict_error_strategy_succeeds(self):
        result = merge_tile_maps([_map(A), _map(B)], on_conflict="error")
        assert len(result) == 2


# ---------------------------------------------------------------------------
# tile_map_stats
# ---------------------------------------------------------------------------

class TestTileMapStats:
    def test_empty_map(self):
        stats = tile_map_stats({})
        assert stats["count"] == 0
        assert stats["total_bytes"] == 0
        assert stats["zoom_levels"] == []

    def test_count_correct(self):
        stats = tile_map_stats(_map(A, B, C))
        assert stats["count"] == 3

    def test_total_bytes_correct(self):
        m = {A: b"ab", B: b"cde"}
        stats = tile_map_stats(m)
        assert stats["total_bytes"] == 5

    def test_zoom_levels_sorted(self):
        m = {(12, 0, 0): b"x", (10, 0, 0): b"y", (11, 0, 0): b"z"}
        stats = tile_map_stats(m)
        assert stats["zoom_levels"] == [10, 11, 12]

    def test_single_zoom_level(self):
        stats = tile_map_stats(_map(A, B))
        assert stats["zoom_levels"] == [10]
