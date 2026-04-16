"""Tests for tilestitch.bbox_splitter."""

import pytest

from tilestitch.bbox_splitter import BBoxGrid, BBoxSplitError, bbox_area, split_bbox


SAMPLE: tuple = (-10.0, -5.0, 10.0, 5.0)  # 20 wide, 10 tall


class TestSplitBbox:
    def test_returns_bbox_grid(self):
        result = split_bbox(SAMPLE, rows=1, cols=1)
        assert isinstance(result, BBoxGrid)

    def test_single_cell_equals_input(self):
        result = split_bbox(SAMPLE, rows=1, cols=1)
        assert len(result) == 1
        assert result[0] == pytest.approx(SAMPLE)

    def test_2x2_produces_four_cells(self):
        result = split_bbox(SAMPLE, rows=2, cols=2)
        assert len(result) == 4

    def test_rows_cols_stored(self):
        result = split_bbox(SAMPLE, rows=3, cols=4)
        assert result.rows == 3
        assert result.cols == 4

    def test_cell_count_matches_rows_times_cols(self):
        result = split_bbox(SAMPLE, rows=5, cols=3)
        assert len(result) == 15

    def test_cells_cover_full_longitude_range(self):
        result = split_bbox(SAMPLE, rows=1, cols=4)
        assert result.cells[0][0] == pytest.approx(SAMPLE[0])   # west
        assert result.cells[-1][2] == pytest.approx(SAMPLE[2])  # east

    def test_cells_cover_full_latitude_range(self):
        result = split_bbox(SAMPLE, rows=4, cols=1)
        assert result.cells[0][1] == pytest.approx(SAMPLE[1])   # south
        assert result.cells[-1][3] == pytest.approx(SAMPLE[3])  # north

    def test_cells_are_equal_area(self):
        result = split_bbox(SAMPLE, rows=2, cols=2)
        areas = [bbox_area(c) for c in result.cells]
        assert all(a == pytest.approx(areas[0]) for a in areas)

    def test_zero_rows_raises(self):
        with pytest.raises(BBoxSplitError):
            split_bbox(SAMPLE, rows=0, cols=1)

    def test_zero_cols_raises(self):
        with pytest.raises(BBoxSplitError):
            split_bbox(SAMPLE, rows=1, cols=0)

    def test_negative_rows_raises(self):
        with pytest.raises(BBoxSplitError):
            split_bbox(SAMPLE, rows=-1, cols=1)

    def test_east_not_greater_than_west_raises(self):
        with pytest.raises(BBoxSplitError):
            split_bbox((10.0, -5.0, -10.0, 5.0), rows=1, cols=1)

    def test_north_not_greater_than_south_raises(self):
        with pytest.raises(BBoxSplitError):
            split_bbox((-10.0, 5.0, 10.0, -5.0), rows=1, cols=1)


class TestBboxArea:
    def test_known_area(self):
        assert bbox_area((-10.0, -5.0, 10.0, 5.0)) == pytest.approx(200.0)

    def test_unit_box(self):
        assert bbox_area((0.0, 0.0, 1.0, 1.0)) == pytest.approx(1.0)
