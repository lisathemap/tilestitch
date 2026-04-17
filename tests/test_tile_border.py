"""Tests for tilestitch.tile_border."""
import pytest
from PIL import Image

from tilestitch.tile_border import (
    BorderConfig,
    BorderError,
    add_border,
    border_config_from_env,
)


def _blank(size: int = 64) -> Image.Image:
    return Image.new("RGBA", (size, size), (200, 200, 200, 255))


class TestBorderConfig:
    def test_defaults(self):
        cfg = BorderConfig()
        assert cfg.width == 1
        assert cfg.colour == (255, 0, 0, 255)

    def test_zero_width_raises(self):
        with pytest.raises(BorderError):
            BorderConfig(width=0)

    def test_negative_width_raises(self):
        with pytest.raises(BorderError):
            BorderConfig(width=-1)

    def test_short_colour_raises(self):
        with pytest.raises(BorderError):
            BorderConfig(colour=(255, 0, 0))  # type: ignore[arg-type]

    def test_channel_out_of_range_raises(self):
        with pytest.raises(BorderError):
            BorderConfig(colour=(256, 0, 0, 255))

    def test_valid_custom(self):
        cfg = BorderConfig(width=3, colour=(0, 255, 0, 128))
        assert cfg.width == 3


class TestAddBorder:
    def test_returns_image(self):
        result = add_border(_blank(), BorderConfig())
        assert isinstance(result, Image.Image)

    def test_size_unchanged(self):
        img = _blank(64)
        result = add_border(img, BorderConfig(width=2))
        assert result.size == img.size

    def test_border_pixels_set(self):
        img = _blank(32)
        colour = (0, 128, 255, 255)
        result = add_border(img, BorderConfig(width=1, colour=colour))
        assert result.getpixel((0, 0)) == colour
        assert result.getpixel((31, 31)) == colour

    def test_interior_pixel_unchanged(self):
        img = _blank(32)
        result = add_border(img, BorderConfig(width=1))
        # centre pixel should still be the original grey
        assert result.getpixel((16, 16)) == (200, 200, 200, 255)

    def test_original_not_mutated(self):
        img = _blank(32)
        original_pixel = img.getpixel((0, 0))
        add_border(img, BorderConfig())
        assert img.getpixel((0, 0)) == original_pixel

    def test_wide_border(self):
        img = _blank(32)
        colour = (10, 20, 30, 255)
        result = add_border(img, BorderConfig(width=5, colour=colour))
        assert result.getpixel((2, 2)) == colour


class TestBorderConfigFromEnv:
    def test_defaults(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_BORDER_WIDTH", raising=False)
        monkeypatch.delenv("TILESTITCH_BORDER_COLOUR", raising=False)
        cfg = border_config_from_env()
        assert cfg.width == 1

    def test_reads_width(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_BORDER_WIDTH", "4")
        monkeypatch.delenv("TILESTITCH_BORDER_COLOUR", raising=False)
        cfg = border_config_from_env()
        assert cfg.width == 4

    def test_reads_colour(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_BORDER_WIDTH", raising=False)
        monkeypatch.setenv("TILESTITCH_BORDER_COLOUR", "0,255,0,200")
        cfg = border_config_from_env()
        assert cfg.colour == (0, 255, 0, 200)

    def test_bad_colour_raises(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_BORDER_COLOUR", "0,255,0")
        with pytest.raises(BorderError):
            border_config_from_env()
