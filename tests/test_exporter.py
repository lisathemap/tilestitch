"""Tests for tilestitch.exporter module."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from tilestitch.exporter import (
    _build_world_file_content,
    export_png,
    export_geotiff,
)
from tilestitch.tile_math import TileBounds


SAMPLE_BOUNDS = TileBounds(north=51.5, south=51.0, west=-0.5, east=0.0)


def _make_image(width: int = 256, height: int = 256) -> Image.Image:
    img = Image.new("RGB", (width, height), color=(100, 149, 237))
    return img


class TestBuildWorldFileContent:
    def test_returns_six_lines(self):
        content = _build_world_file_content(SAMPLE_BOUNDS, 256, 256)
        lines = [l for l in content.strip().split("\n") if l]
        assert len(lines) == 6

    def test_pixel_size_x_positive(self):
        content = _build_world_file_content(SAMPLE_BOUNDS, 256, 256)
        lines = content.strip().split("\n")
        pixel_size_x = float(lines[0])
        assert pixel_size_x > 0

    def test_pixel_size_y_negative(self):
        content = _build_world_file_content(SAMPLE_BOUNDS, 256, 256)
        lines = content.strip().split("\n")
        pixel_size_y = float(lines[3])
        assert pixel_size_y < 0

    def test_top_left_coordinates(self):
        content = _build_world_file_content(SAMPLE_BOUNDS, 256, 256)
        lines = content.strip().split("\n")
        top_left_x = float(lines[4])
        top_left_y = float(lines[5])
        assert top_left_x == pytest.approx(SAMPLE_BOUNDS.west, rel=1e-6)
        assert top_left_y == pytest.approx(SAMPLE_BOUNDS.north, rel=1e-6)

    def test_pixel_sizes_match_extent(self):
        bounds = TileBounds(north=2.0, south=0.0, west=0.0, east=4.0)
        content = _build_world_file_content(bounds, 400, 200)
        lines = content.strip().split("\n")
        assert float(lines[0]) == pytest.approx(4.0 / 400, rel=1e-6)
        assert float(lines[3]) == pytest.approx(-2.0 / 200, rel=1e-6)


class TestExportPng:
    def test_creates_file(self, tmp_path):
        img = _make_image()
        out = tmp_path / "output.png"
        result = export_png(img, out)
        assert result == out
        assert out.exists()

    def test_no_world_file_without_bounds(self, tmp_path):
        img = _make_image()
        out = tmp_path / "output.png"
        export_png(img, out)
        assert not (tmp_path / "output.pgw").exists()

    def test_world_file_created_with_bounds(self, tmp_path):
        img = _make_image()
        out = tmp_path / "output.png"
        export_png(img, out, bounds=SAMPLE_BOUNDS)
        pgw = tmp_path / "output.pgw"
        assert pgw.exists()
        assert len(pgw.read_text().strip().split("\n")) == 6

    def test_creates_parent_directories(self, tmp_path):
        img = _make_image()
        out = tmp_path / "nested" / "dir" / "output.png"
        export_png(img, out)
        assert out.exists()


class TestExportGeotiff:
    def test_creates_some_output_file(self, tmp_path):
        img = _make_image()
        out = tmp_path / "output.tif"
        result = export_geotiff(img, out, bounds=SAMPLE_BOUNDS)
        assert result.exists()

    def test_output_is_tiff(self, tmp_path):
        img = _make_image()
        out = tmp_path / "output.tif"
        result = export_geotiff(img, out, bounds=SAMPLE_BOUNDS)
        # TIFF magic bytes: II (little-endian) or MM (big-endian)
        magic = result.read_bytes()[:2]
        assert magic in (b"II", b"MM")
