"""Tests for tile_mosaic."""
import pytest
from PIL import Image

from tilestitch.tile_mosaic import (
    MosaicConfig,
    MosaicError,
    apply_mosaic,
    mosaic_config_from_env,
)


def _solid(colour=(255, 0, 0, 255), size=(64, 64)) -> Image.Image:
    img = Image.new("RGBA", size, colour)
    return img


class TestMosaicConfig:
    def test_defaults(self):
        c = MosaicConfig()
        assert c.enabled is True
        assert c.tile_size == 16

    def test_tile_size_stored(self):
        c = MosaicConfig(tile_size=8)
        assert c.tile_size == 8

    def test_zero_tile_size_raises(self):
        with pytest.raises(MosaicError):
            MosaicConfig(tile_size=0)

    def test_one_tile_size_raises(self):
        with pytest.raises(MosaicError):
            MosaicConfig(tile_size=1)

    def test_two_tile_size_valid(self):
        c = MosaicConfig(tile_size=2)
        assert c.tile_size == 2

    def test_negative_tile_size_raises(self):
        with pytest.raises(MosaicError):
            MosaicConfig(tile_size=-4)


class TestApplyMosaic:
    def test_returns_image(self):
        img = _solid()
        result = apply_mosaic(img, MosaicConfig())
        assert isinstance(result, Image.Image)

    def test_same_size(self):
        img = _solid(size=(64, 64))
        result = apply_mosaic(img, MosaicConfig(tile_size=8))
        assert result.size == (64, 64)

    def test_disabled_returns_original(self):
        img = _solid()
        result = apply_mosaic(img, MosaicConfig(enabled=False))
        assert result is img

    def test_solid_colour_unchanged(self):
        img = _solid(colour=(100, 150, 200, 255))
        result = apply_mosaic(img, MosaicConfig(tile_size=16))
        px = result.convert("RGBA").getpixel((0, 0))
        assert px[0] == pytest.approx(100, abs=2)
        assert px[1] == pytest.approx(150, abs=2)
        assert px[2] == pytest.approx(200, abs=2)

    def test_mode_preserved_rgb(self):
        img = Image.new("RGB", (32, 32), (10, 20, 30))
        result = apply_mosaic(img, MosaicConfig(tile_size=8))
        assert result.mode == "RGB"

    def test_non_square_image(self):
        img = _solid(size=(80, 40))
        result = apply_mosaic(img, MosaicConfig(tile_size=10))
        assert result.size == (80, 40)


class TestMosaicConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_MOSAIC_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_MOSAIC_TILE_SIZE", raising=False)
        c = mosaic_config_from_env()
        assert c.enabled is False
        assert c.tile_size == 16

    def test_enabled_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_MOSAIC_ENABLED", "true")
        c = mosaic_config_from_env()
        assert c.enabled is True

    def test_tile_size_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_MOSAIC_TILE_SIZE", "32")
        c = mosaic_config_from_env()
        assert c.tile_size == 32
