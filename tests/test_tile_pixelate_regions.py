"""Tests for tilestitch.tile_pixelate_regions."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_pixelate_regions import (
    PixelateRegionsConfig,
    PixelateRegionsError,
    apply_pixelate_regions,
)


def _solid(colour: tuple = (100, 150, 200, 255), size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), colour)
    return img


# ---------------------------------------------------------------------------
# PixelateRegionsConfig
# ---------------------------------------------------------------------------

class TestPixelateRegionsConfig:
    def test_defaults(self):
        cfg = PixelateRegionsConfig()
        assert cfg.regions == []
        assert cfg.block_size == 16
        assert cfg.enabled is True

    def test_regions_stored(self):
        cfg = PixelateRegionsConfig(regions=[(0, 0, 10, 10)])
        assert cfg.regions == [(0, 0, 10, 10)]

    def test_block_size_stored(self):
        cfg = PixelateRegionsConfig(block_size=8)
        assert cfg.block_size == 8

    def test_zero_block_size_raises(self):
        with pytest.raises(PixelateRegionsError, match="block_size"):
            PixelateRegionsConfig(block_size=0)

    def test_negative_block_size_raises(self):
        with pytest.raises(PixelateRegionsError):
            PixelateRegionsConfig(block_size=-4)

    def test_degenerate_region_x_raises(self):
        with pytest.raises(PixelateRegionsError, match="degenerate"):
            PixelateRegionsConfig(regions=[(10, 0, 10, 20)])

    def test_degenerate_region_y_raises(self):
        with pytest.raises(PixelateRegionsError, match="degenerate"):
            PixelateRegionsConfig(regions=[(0, 20, 10, 20)])

    def test_wrong_tuple_length_raises(self):
        with pytest.raises(PixelateRegionsError, match="4-tuple"):
            PixelateRegionsConfig(regions=[(0, 0, 10)])  # type: ignore[list-item]

    def test_multiple_valid_regions(self):
        cfg = PixelateRegionsConfig(
            regions=[(0, 0, 8, 8), (16, 16, 32, 32)]
        )
        assert len(cfg.regions) == 2


# ---------------------------------------------------------------------------
# apply_pixelate_regions
# ---------------------------------------------------------------------------

class TestApplyPixelateRegions:
    def test_returns_image(self):
        img = _solid()
        cfg = PixelateRegionsConfig(regions=[(0, 0, 32, 32)])
        result = apply_pixelate_regions(img, cfg)
        assert isinstance(result, Image.Image)

    def test_same_size_preserved(self):
        img = _solid(size=64)
        cfg = PixelateRegionsConfig(regions=[(0, 0, 64, 64)])
        result = apply_pixelate_regions(img, cfg)
        assert result.size == (64, 64)

    def test_disabled_returns_original_unchanged(self):
        img = _solid(colour=(10, 20, 30, 255))
        cfg = PixelateRegionsConfig(regions=[(0, 0, 64, 64)], enabled=False)
        result = apply_pixelate_regions(img, cfg)
        assert result is img

    def test_no_regions_returns_original(self):
        img = _solid()
        cfg = PixelateRegionsConfig(regions=[])
        result = apply_pixelate_regions(img, cfg)
        assert result is img

    def test_out_of_bounds_region_clamped(self):
        img = _solid(size=32)
        cfg = PixelateRegionsConfig(regions=[(-10, -10, 100, 100)])
        result = apply_pixelate_regions(img, cfg)
        assert result.size == (32, 32)

    def test_pixelated_region_differs_from_original(self):
        # Use a gradient so pixelation is visible
        img = Image.new("RGBA", (64, 64))
        for x in range(64):
            for y in range(64):
                img.putpixel((x, y), (x * 4 % 256, y * 4 % 256, 128, 255))
        cfg = PixelateRegionsConfig(regions=[(0, 0, 64, 64)], block_size=8)
        result = apply_pixelate_regions(img, cfg)
        # After block pixelation the image should not be identical pixel-for-pixel
        assert list(result.getdata()) != list(img.getdata())

    def test_multiple_regions_applied(self):
        img = _solid(size=64)
        cfg = PixelateRegionsConfig(
            regions=[(0, 0, 16, 16), (32, 32, 48, 48)], block_size=4
        )
        result = apply_pixelate_regions(img, cfg)
        assert result.size == (64, 64)
