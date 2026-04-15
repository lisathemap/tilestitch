"""Tests for tilestitch.stitcher."""

from __future__ import annotations

import io
import os
import tempfile
from typing import Dict, Tuple
from unittest.mock import patch

import pytest

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    pytest.skip("Pillow not installed", allow_module_level=True)

from tilestitch.tile_math import TileBounds
from tilestitch.stitcher import stitch_tiles, save_image


def _make_png(color: Tuple[int, int, int, int] = (255, 0, 0, 255)) -> bytes:
    """Return raw PNG bytes for a 256x256 solid-colour tile."""
    img = Image.new("RGBA", (256, 256), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestStitchTiles:
    def _bounds(self, min_x=0, min_y=0, max_x=1, max_y=1, zoom=10):
        return TileBounds(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y, zoom=zoom)

    def test_canvas_size_single_tile(self):
        bounds = self._bounds(min_x=5, min_y=5, max_x=5, max_y=5)
        data = {(5, 5): _make_png()}
        img = stitch_tiles(data, bounds)
        assert img.size == (256, 256)

    def test_canvas_size_2x2(self):
        bounds = self._bounds(min_x=0, min_y=0, max_x=1, max_y=1)
        data = {
            (0, 0): _make_png((255, 0, 0, 255)),
            (1, 0): _make_png((0, 255, 0, 255)),
            (0, 1): _make_png((0, 0, 255, 255)),
            (1, 1): _make_png((255, 255, 0, 255)),
        }
        img = stitch_tiles(data, bounds)
        assert img.size == (512, 512)

    def test_pixel_placed_correctly(self):
        """Top-left tile should be red; bottom-right should be blue."""
        bounds = self._bounds(min_x=0, min_y=0, max_x=1, max_y=1)
        data = {
            (0, 0): _make_png((255, 0, 0, 255)),
            (1, 1): _make_png((0, 0, 255, 255)),
        }
        img = stitch_tiles(data, bounds)
        assert img.getpixel((0, 0))[:3] == (255, 0, 0)
        assert img.getpixel((256, 256))[:3] == (0, 0, 255)

    def test_corrupt_tile_uses_placeholder(self):
        bounds = self._bounds(min_x=0, min_y=0, max_x=0, max_y=0)
        data = {(0, 0): b"not-an-image"}
        img = stitch_tiles(data, bounds)
        assert img.size == (256, 256)
        # placeholder is grey
        r, g, b, _ = img.getpixel((0, 0))
        assert r == g == b == 200

    def test_returns_rgba(self):
        bounds = self._bounds(min_x=0, min_y=0, max_x=0, max_y=0)
        img = stitch_tiles({(0, 0): _make_png()}, bounds)
        assert img.mode == "RGBA"


class TestSaveImage:
    def test_saves_png(self):
        img = Image.new("RGBA", (256, 256), (0, 128, 255, 255))
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            save_image(img, path, fmt="PNG")
            loaded = Image.open(path)
            assert loaded.size == (256, 256)
        finally:
            os.unlink(path)

    def test_saves_jpeg(self):
        img = Image.new("RGB", (256, 256), (0, 128, 255))
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            path = f.name
        try:
            save_image(img, path, fmt="JPEG")
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)
