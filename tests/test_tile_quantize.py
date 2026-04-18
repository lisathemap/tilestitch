"""Tests for tilestitch.tile_quantize."""
import os
import pytest
from PIL import Image

from tilestitch.tile_quantize import (
    QuantizeConfig,
    QuantizeError,
    apply_quantize,
    quantize_config_from_env,
)


def _solid(mode: str = "RGB", colour=(100, 150, 200)) -> Image.Image:
    img = Image.new(mode, (64, 64), colour)
    return img


class TestQuantizeConfig:
    def test_defaults(self):
        cfg = QuantizeConfig()
        assert cfg.enabled is False
        assert cfg.colours == 256
        assert cfg.dither is True

    def test_colours_stored(self):
        cfg = QuantizeConfig(colours=16)
        assert cfg.colours == 16

    def test_one_colour_raises(self):
        with pytest.raises(QuantizeError):
            QuantizeConfig(colours=1)

    def test_zero_colours_raises(self):
        with pytest.raises(QuantizeError):
            QuantizeConfig(colours=0)

    def test_257_colours_raises(self):
        with pytest.raises(QuantizeError):
            QuantizeConfig(colours=257)

    def test_two_colours_valid(self):
        cfg = QuantizeConfig(colours=2)
        assert cfg.colours == 2

    def test_256_colours_valid(self):
        cfg = QuantizeConfig(colours=256)
        assert cfg.colours == 256


class TestApplyQuantize:
    def test_returns_image_when_disabled(self):
        img = _solid()
        cfg = QuantizeConfig(enabled=False)
        result = apply_quantize(img, cfg)
        assert result is img

    def test_returns_image_when_enabled(self):
        img = _solid()
        cfg = QuantizeConfig(enabled=True, colours=16)
        result = apply_quantize(img, cfg)
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self):
        img = _solid()
        cfg = QuantizeConfig(enabled=True, colours=32)
        result = apply_quantize(img, cfg)
        assert result.size == img.size

    def test_rgba_input_preserved(self):
        img = _solid(mode="RGBA", colour=(100, 150, 200, 255))
        cfg = QuantizeConfig(enabled=True, colours=64)
        result = apply_quantize(img, cfg)
        assert result.mode == "RGBA"

    def test_rgb_input_preserved(self):
        img = _solid(mode="RGB")
        cfg = QuantizeConfig(enabled=True, colours=64)
        result = apply_quantize(img, cfg)
        assert result.mode == "RGB"


class TestQuantizeConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_QUANTIZE_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_QUANTIZE_COLOURS", raising=False)
        monkeypatch.delenv("TILESTITCH_QUANTIZE_DITHER", raising=False)
        cfg = quantize_config_from_env()
        assert cfg.enabled is False
        assert cfg.colours == 256
        assert cfg.dither is True

    def test_reads_enabled(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_QUANTIZE_ENABLED", "true")
        cfg = quantize_config_from_env()
        assert cfg.enabled is True

    def test_reads_colours(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_QUANTIZE_COLOURS", "32")
        cfg = quantize_config_from_env()
        assert cfg.colours == 32

    def test_dither_false(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_QUANTIZE_DITHER", "false")
        cfg = quantize_config_from_env()
        assert cfg.dither is False
