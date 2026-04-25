"""Tests for tilestitch.tile_pixelsort."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_pixelsort import (
    PixelSortConfig,
    PixelSortError,
    apply_pixelsort,
)


def _solid(r: int = 128, g: int = 64, b: int = 32, size: int = 16) -> Image.Image:
    img = Image.new("RGB", (size, size), (r, g, b))
    return img


# ---------------------------------------------------------------------------
# PixelSortConfig
# ---------------------------------------------------------------------------

class TestPixelSortConfig:
    def test_defaults(self):
        cfg = PixelSortConfig()
        assert cfg.enabled is True
        assert cfg.axis == "x"
        assert cfg.sort_key == "brightness"
        assert cfg.threshold_low == pytest.approx(0.2)
        assert cfg.threshold_high == pytest.approx(0.8)
        assert cfg.reverse is False

    def test_invalid_axis_raises(self):
        with pytest.raises(PixelSortError, match="axis"):
            PixelSortConfig(axis="z")

    def test_invalid_sort_key_raises(self):
        with pytest.raises(PixelSortError, match="sort_key"):
            PixelSortConfig(sort_key="luminance")

    def test_threshold_low_below_zero_raises(self):
        with pytest.raises(PixelSortError, match="threshold_low"):
            PixelSortConfig(threshold_low=-0.1)

    def test_threshold_high_above_one_raises(self):
        with pytest.raises(PixelSortError, match="threshold_high"):
            PixelSortConfig(threshold_high=1.1)

    def test_threshold_low_equals_high_raises(self):
        with pytest.raises(PixelSortError, match="threshold_low must be less"):
            PixelSortConfig(threshold_low=0.5, threshold_high=0.5)

    def test_threshold_low_above_high_raises(self):
        with pytest.raises(PixelSortError, match="threshold_low must be less"):
            PixelSortConfig(threshold_low=0.8, threshold_high=0.2)

    def test_axis_y_valid(self):
        cfg = PixelSortConfig(axis="y")
        assert cfg.axis == "y"

    def test_sort_key_hue_valid(self):
        cfg = PixelSortConfig(sort_key="hue")
        assert cfg.sort_key == "hue"

    def test_sort_key_saturation_valid(self):
        cfg = PixelSortConfig(sort_key="saturation")
        assert cfg.sort_key == "saturation"

    def test_reverse_stored(self):
        cfg = PixelSortConfig(reverse=True)
        assert cfg.reverse is True

    def test_threshold_boundaries_valid(self):
        cfg = PixelSortConfig(threshold_low=0.0, threshold_high=1.0)
        assert cfg.threshold_low == 0.0
        assert cfg.threshold_high == 1.0


# ---------------------------------------------------------------------------
# apply_pixelsort
# ---------------------------------------------------------------------------

class TestApplyPixelsort:
    def test_returns_image(self):
        img = _solid()
        result = apply_pixelsort(img, PixelSortConfig())
        assert isinstance(result, Image.Image)

    def test_output_size_preserved(self):
        img = _solid(size=32)
        result = apply_pixelsort(img, PixelSortConfig())
        assert result.size == img.size

    def test_output_is_rgba(self):
        img = _solid()
        result = apply_pixelsort(img, PixelSortConfig())
        assert result.mode == "RGBA"

    def test_axis_y_does_not_raise(self):
        img = _solid()
        result = apply_pixelsort(img, PixelSortConfig(axis="y"))
        assert result.size == img.size

    def test_hue_key_does_not_raise(self):
        img = _solid()
        result = apply_pixelsort(img, PixelSortConfig(sort_key="hue"))
        assert isinstance(result, Image.Image)

    def test_saturation_key_does_not_raise(self):
        img = _solid()
        result = apply_pixelsort(img, PixelSortConfig(sort_key="saturation"))
        assert isinstance(result, Image.Image)

    def test_reverse_does_not_raise(self):
        img = _solid()
        result = apply_pixelsort(img, PixelSortConfig(reverse=True))
        assert isinstance(result, Image.Image)

    def test_narrow_threshold_leaves_most_pixels_unchanged(self):
        """With a very tight threshold nothing in a solid image gets sorted."""
        img = _solid(r=200, g=200, b=200, size=8)
        cfg = PixelSortConfig(threshold_low=0.0, threshold_high=0.01)
        result = apply_pixelsort(img, cfg)
        assert result.size == img.size
