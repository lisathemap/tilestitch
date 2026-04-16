"""Tests for tilestitch.tile_sorter and tilestitch.tile_sorter_config."""

from __future__ import annotations

import pytest

from tilestitch.tile_math import TileBounds
from tilestitch.tile_sorter import (
    SortOrder,
    SortOrderError,
    sort_tiles,
)
from tilestitch.tile_sorter_config import TileSorterConfig, tile_sorter_config_from_env


@pytest.fixture()
def bounds() -> TileBounds:
    return TileBounds(x_min=0, x_max=4, y_min=0, y_max=4, zoom=3)


@pytest.fixture()
def keys() -> list[tuple[int, int, int]]:
    return [(3, 0, 1), (3, 1, 0), (3, 0, 0), (3, 1, 1)]


class TestSortOrderFromString:
    def test_row_major(self):
        assert SortOrder.from_string("row_major") == SortOrder.ROW_MAJOR

    def test_col_major(self):
        assert SortOrder.from_string("col_major") == SortOrder.COL_MAJOR

    def test_hilbert(self):
        assert SortOrder.from_string("hilbert") == SortOrder.HILBERT

    def test_case_insensitive(self):
        assert SortOrder.from_string("ROW_MAJOR") == SortOrder.ROW_MAJOR

    def test_whitespace_stripped(self):
        assert SortOrder.from_string("  hilbert  ") == SortOrder.HILBERT

    def test_unknown_raises(self):
        with pytest.raises(SortOrderError):
            SortOrder.from_string("diagonal")


class TestSortTilesRowMajor:
    def test_sorted_by_y_then_x(self, keys, bounds):
        result = sort_tiles(keys, bounds, SortOrder.ROW_MAJOR)
        ys = [t[2] for t in result]
        assert ys == sorted(ys)

    def test_returns_all_keys(self, keys, bounds):
        result = sort_tiles(keys, bounds, SortOrder.ROW_MAJOR)
        assert set(result) == set(keys)

    def test_empty_input(self, bounds):
        assert sort_tiles([], bounds, SortOrder.ROW_MAJOR) == []


class TestSortTilesColMajor:
    def test_sorted_by_x_then_y(self, keys, bounds):
        result = sort_tiles(keys, bounds, SortOrder.COL_MAJOR)
        xs = [t[1] for t in result]
        assert xs == sorted(xs)

    def test_returns_all_keys(self, keys, bounds):
        result = sort_tiles(keys, bounds, SortOrder.COL_MAJOR)
        assert set(result) == set(keys)


class TestSortTilesHilbert:
    def test_returns_all_keys(self, keys, bounds):
        result = sort_tiles(keys, bounds, SortOrder.HILBERT)
        assert set(result) == set(keys)

    def test_single_tile(self, bounds):
        single = [(3, 0, 0)]
        assert sort_tiles(single, bounds, SortOrder.HILBERT) == single


class TestTileSorterConfig:
    def test_default_order(self):
        cfg = TileSorterConfig()
        assert cfg.order == SortOrder.ROW_MAJOR

    def test_custom_order(self):
        cfg = TileSorterConfig(order=SortOrder.HILBERT)
        assert cfg.order == SortOrder.HILBERT

    def test_invalid_type_raises(self):
        with pytest.raises(TypeError):
            TileSorterConfig(order="row_major")  # type: ignore[arg-type]

    def test_from_env_default(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_SORT_ORDER", raising=False)
        cfg = tile_sorter_config_from_env()
        assert cfg.order == SortOrder.ROW_MAJOR

    def test_from_env_hilbert(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SORT_ORDER", "hilbert")
        cfg = tile_sorter_config_from_env()
        assert cfg.order == SortOrder.HILBERT
