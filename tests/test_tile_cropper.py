"""Tests for tilestitch.tile_cropper."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_math import TileBounds
from tilestitch.tile_cropper import CropBox, CropError, compute_crop_box, crop_image


def _bounds(x_min=0, y_min=0, x_max=1, y_max=1, zoom=10) -> TileBounds:
    return TileBounds(x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max, zoom=zoom)


def _canvas(bounds: TileBounds, tile_size: int = 256) -> Image.Image:
    w = (bounds.x_max - bounds.x_min + 1) * tile_size
    h = (bounds.y_max - bounds.y_min + 1) * tile_size
    return Image.new("RGB", (w, h), color=(128, 128, 128))


class TestComputeCropBox:
    def test_returns_crop_box(self):
        bounds = _bounds(x_min=0, y_min=0, x_max=0, y_max=0, zoom=1)
        from tilestitch.tile_math import tile_to_lat_lon
        lat0, lon0 = tile_to_lat_lon(0, 0, 1)
        lat1, lon1 = tile_to_lat_lon(1, 1, 1)
        bbox = (lon0, lat1, lon1, lat0)
        box = compute_crop_box(bbox, bounds, tile_size=256)
        assert isinstance(box, CropBox)

    def test_full_canvas_returns_full_box(self):
        zoom = 1
        bounds = _bounds(x_min=0, y_min=0, x_max=0, y_max=0, zoom=zoom)
        from tilestitch.tile_math import tile_to_lat_lon
        lat_top, lon_left = tile_to_lat_lon(0, 0, zoom)
        lat_bot, lon_right = tile_to_lat_lon(1, 1, zoom)
        bbox = (lon_left, lat_bot, lon_right, lat_top)
        box = compute_crop_box(bbox, bounds, tile_size=256)
        assert box.left == 0
        assert box.upper == 0
        assert box.right == 256
        assert box.lower == 256

    def test_crop_box_area_positive(self):
        zoom = 2
        bounds = _bounds(x_min=1, y_min=1, x_max=2, y_max=2, zoom=zoom)
        from tilestitch.tile_math import tile_to_lat_lon
        lat_top, lon_left = tile_to_lat_lon(1, 1, zoom)
        lat_bot, lon_right = tile_to_lat_lon(3, 3, zoom)
        mid_lon = (lon_left + lon_right) / 2
        mid_lat = (lat_top + lat_bot) / 2
        bbox = (lon_left, lat_bot, mid_lon, lat_top)
        box = compute_crop_box(bbox, bounds, tile_size=256)
        assert box.right > box.left
        assert box.lower > box.upper

    def test_as_tuple_length_four(self):
        box = CropBox(left=10, upper=20, right=100, lower=200)
        t = box.as_tuple()
        assert len(t) == 4
        assert t == (10, 20, 100, 200)


class TestCropImage:
    def test_returns_image(self):
        zoom = 1
        bounds = _bounds(x_min=0, y_min=0, x_max=0, y_max=0, zoom=zoom)
        from tilestitch.tile_math import tile_to_lat_lon
        lat_top, lon_left = tile_to_lat_lon(0, 0, zoom)
        lat_bot, lon_right = tile_to_lat_lon(1, 1, zoom)
        bbox = (lon_left, lat_bot, lon_right, lat_top)
        img = _canvas(bounds)
        result = crop_image(img, bbox, bounds, tile_size=256)
        assert isinstance(result, Image.Image)

    def test_cropped_size_smaller_or_equal(self):
        zoom = 1
        bounds = _bounds(x_min=0, y_min=0, x_max=1, y_max=1, zoom=zoom)
        from tilestitch.tile_math import tile_to_lat_lon
        lat_top, lon_left = tile_to_lat_lon(0, 0, zoom)
        lat_bot, lon_right = tile_to_lat_lon(2, 2, zoom)
        mid_lon = (lon_left + lon_right) / 2
        mid_lat = (lat_top + lat_bot) / 2
        bbox = (lon_left, mid_lat, mid_lon, lat_top)
        img = _canvas(bounds)
        result = crop_image(img, bbox, bounds, tile_size=256)
        assert result.width <= img.width
        assert result.height <= img.height
