"""Tests for tilestitch.tile_sharpen."""

import pytest
from PIL import Image

from tilestitch.tile_sharpen import (
    SharpenConfig,
    SharpenError,
    apply_sharpen,
    sharpen_config_from_env,
)


def _solid(colour: tuple = (128, 128, 128), size: int = 64) -> Image.Image:
    img = Image.new("RGB", (size, size), colour)
    return img


class TestSharpenConfig:
    def test_defaults(self):
        cfg = SharpenConfig()
        assert cfg.enabled is False
        assert cfg.factor == 1.0

    def test_zero_factor_raises(self):
        with pytest.raises(SharpenError):
            SharpenConfig(factor=0.0)

    def test_negative_factor_raises(self):
        with pytest.raises(SharpenError):
            SharpenConfig(factor=-0.5)

    def test_valid_factor_stored(self):
        cfg = SharpenConfig(factor=2.5)
        assert cfg.factor == 2.5


class TestApplySharpen:
    def test_disabled_returns_same_object(self):
        img = _solid()
        cfg = SharpenConfig(enabled=False, factor=2.0)
        result = apply_sharpen(img, cfg)
        assert result is img

    def test_factor_one_returns_same_object(self):
        img = _solid()
        cfg = SharpenConfig(enabled=True, factor=1.0)
        result = apply_sharpen(img, cfg)
        assert result is img

    def test_enabled_returns_image(self):
        img = _solid()
        cfg = SharpenConfig(enabled=True, factor=2.0)
        result = apply_sharpen(img, cfg)
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self):
        img = _solid(size=64)
        cfg = SharpenConfig(enabled=True, factor=3.0)
        result = apply_sharpen(img, cfg)
        assert result.size == img.size

    def test_output_mode_unchanged(self):
        img = _solid()
        cfg = SharpenConfig(enabled=True, factor=2.0)
        result = apply_sharpen(img, cfg)
        assert result.mode == img.mode


class TestSharpenConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_SHARPEN_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_SHARPEN_FACTOR", raising=False)
        cfg = sharpen_config_from_env()
        assert cfg.enabled is False

    def test_enabled_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SHARPEN_ENABLED", "true")
        monkeypatch.setenv("TILESTITCH_SHARPEN_FACTOR", "3.0")
        cfg = sharpen_config_from_env()
        assert cfg.enabled is True
        assert cfg.factor == 3.0
