"""Tests for tilestitch.tile_brightness."""
import pytest
from PIL import Image

from tilestitch.tile_brightness import (
    BrightnessConfig,
    BrightnessError,
    adjust_brightness,
    brightness_config_from_env,
)


def _solid(r: int, g: int, b: int, size: int = 4) -> Image.Image:
    img = Image.new("RGB", (size, size), (r, g, b))
    return img


class TestBrightnessConfig:
    def test_defaults(self):
        cfg = BrightnessConfig()
        assert cfg.brightness == 1.0
        assert cfg.contrast == 1.0

    def test_zero_brightness_raises(self):
        with pytest.raises(BrightnessError):
            BrightnessConfig(brightness=0.0)

    def test_negative_brightness_raises(self):
        with pytest.raises(BrightnessError):
            BrightnessConfig(brightness=-0.5)

    def test_brightness_above_max_raises(self):
        with pytest.raises(BrightnessError):
            BrightnessConfig(brightness=5.0)

    def test_zero_contrast_raises(self):
        with pytest.raises(BrightnessError):
            BrightnessConfig(contrast=0.0)

    def test_valid_custom_values(self):
        cfg = BrightnessConfig(brightness=1.5, contrast=2.0)
        assert cfg.brightness == 1.5
        assert cfg.contrast == 2.0


class TestAdjustBrightness:
    def test_identity_returns_same_size(self):
        img = _solid(100, 100, 100)
        cfg = BrightnessConfig(brightness=1.0, contrast=1.0)
        out = adjust_brightness(img, cfg)
        assert out.size == img.size

    def test_brightness_increase_lightens_image(self):
        img = _solid(100, 100, 100)
        cfg = BrightnessConfig(brightness=2.0)
        out = adjust_brightness(img, cfg)
        pixel = out.getpixel((0, 0))
        assert pixel[0] > 100

    def test_brightness_decrease_darkens_image(self):
        img = _solid(100, 100, 100)
        cfg = BrightnessConfig(brightness=0.5)
        out = adjust_brightness(img, cfg)
        pixel = out.getpixel((0, 0))
        assert pixel[0] < 100

    def test_returns_pil_image(self):
        img = _solid(80, 80, 80)
        cfg = BrightnessConfig()
        out = adjust_brightness(img, cfg)
        assert isinstance(out, Image.Image)


class TestBrightnessConfigFromEnv:
    def test_defaults_when_env_absent(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_BRIGHTNESS", raising=False)
        monkeypatch.delenv("TILESTITCH_CONTRAST", raising=False)
        cfg = brightness_config_from_env()
        assert cfg.brightness == 1.0
        assert cfg.contrast == 1.0

    def test_reads_brightness_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_BRIGHTNESS", "1.8")
        monkeypatch.delenv("TILESTITCH_CONTRAST", raising=False)
        cfg = brightness_config_from_env()
        assert cfg.brightness == pytest.approx(1.8)

    def test_reads_contrast_from_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_BRIGHTNESS", raising=False)
        monkeypatch.setenv("TILESTITCH_CONTRAST", "0.9")
        cfg = brightness_config_from_env()
        assert cfg.contrast == pytest.approx(0.9)
