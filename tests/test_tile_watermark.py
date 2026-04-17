"""Tests for tilestitch.tile_watermark."""
import pytest
from PIL import Image

from tilestitch.tile_watermark import (
    WatermarkConfig,
    WatermarkError,
    apply_watermark,
    watermark_config_from_env,
)


def _blank(width: int = 256, height: int = 256) -> Image.Image:
    return Image.new("RGB", (width, height), (200, 200, 200))


class TestWatermarkConfig:
    def test_defaults(self):
        cfg = WatermarkConfig(text="hello")
        assert cfg.opacity == 0.5
        assert cfg.font_size == 14
        assert cfg.position == "bottom-right"
        assert cfg.margin == 8

    def test_empty_text_raises(self):
        with pytest.raises(WatermarkError, match="empty"):
            WatermarkConfig(text="   ")

    def test_zero_opacity_raises(self):
        with pytest.raises(WatermarkError, match="opacity"):
            WatermarkConfig(text="hi", opacity=0.0)

    def test_opacity_above_one_raises(self):
        with pytest.raises(WatermarkError, match="opacity"):
            WatermarkConfig(text="hi", opacity=1.1)

    def test_opacity_one_valid(self):
        cfg = WatermarkConfig(text="hi", opacity=1.0)
        assert cfg.opacity == 1.0

    def test_small_font_raises(self):
        with pytest.raises(WatermarkError, match="font_size"):
            WatermarkConfig(text="hi", font_size=5)

    def test_minimum_font_size_ok(self):
        cfg = WatermarkConfig(text="hi", font_size=6)
        assert cfg.font_size == 6

    def test_invalid_position_raises(self):
        with pytest.raises(WatermarkError, match="position"):
            WatermarkConfig(text="hi", position="center")

    def test_valid_positions(self):
        for pos in ("top-left", "top-right", "bottom-left", "bottom-right"):
            cfg = WatermarkConfig(text="hi", position=pos)
            assert cfg.position == pos

    def test_negative_margin_raises(self):
        with pytest.raises(WatermarkError, match="margin"):
            WatermarkConfig(text="hi", margin=-1)

    def test_zero_margin_ok(self):
        cfg = WatermarkConfig(text="hi", margin=0)
        assert cfg.margin == 0


class TestApplyWatermark:
    def test_returns_image(self):
        img = _blank()
        cfg = WatermarkConfig(text="test")
        result = apply_watermark(img, cfg)
        assert isinstance(result, Image.Image)

    def test_same_size(self):
        img = _blank(300, 200)
        cfg = WatermarkConfig(text="test")
        result = apply_watermark(img, cfg)
        assert result.size == img.size

    def test_original_unchanged(self):
        img = _blank()
        original_pixels = list(img.getdata())
        cfg = WatermarkConfig(text="test")
        apply_watermark(img, cfg)
        assert list(img.getdata()) == original_pixels

    def test_all_positions(self):
        for pos in ("top-left", "top-right", "bottom-left", "bottom-right"):
            img = _blank()
            cfg = WatermarkConfig(text="X", position=pos)
            result = apply_watermark(img, cfg)
            assert result.size == img.size

    def test_rgba_input(self):
        img = Image.new("RGBA", (256, 256), (100, 100, 100, 255))
        cfg = WatermarkConfig(text="rgba test")
        result = apply_watermark(img, cfg)
        assert result.mode == "RGBA"


def test_watermark_config_from_env(monkeypatch):
    monkeypatch.setenv("TILESTITCH_WATERMARK_TEXT", "© OpenStreetMap")
    monkeypatch.setenv("TILESTITCH_WATERMARK_OPACITY", "0.8")
    monkeypatch.setenv("TILESTITCH_WATERMARK_FONT_SIZE", "18")
    monkeypatch.setenv("TILESTITCH_WATERMARK_POSITION", "top-left")
    monkeypatch.setenv("TILESTITCH_WATERMARK_MARGIN", "4")
    cfg = watermark_config_from_env()
    assert cfg.text == "© OpenStreetMap"
    assert cfg.opacity == 0.8
    assert cfg.font_size == 18
    assert cfg.position == "top-left"
    assert cfg.margin == 4
