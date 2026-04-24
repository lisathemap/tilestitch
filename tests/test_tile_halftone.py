"""Tests for tilestitch.tile_halftone."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_halftone import (
    HalftoneConfig,
    HalftoneError,
    apply_halftone,
    halftone_config_from_env,
)


def _solid(colour: tuple[int, int, int] = (128, 128, 128), size: int = 64) -> Image.Image:
    img = Image.new("RGB", (size, size), colour)
    return img


class TestHalftoneConfig:
    def test_defaults(self):
        cfg = HalftoneConfig()
        assert cfg.enabled is True
        assert cfg.dot_size == 6
        assert cfg.angle == 45.0
        assert cfg.foreground == "#000000"
        assert cfg.background == "#ffffff"

    def test_dot_size_stored(self):
        cfg = HalftoneConfig(dot_size=10)
        assert cfg.dot_size == 10

    def test_zero_dot_size_raises(self):
        with pytest.raises(HalftoneError):
            HalftoneConfig(dot_size=0)

    def test_negative_dot_size_raises(self):
        with pytest.raises(HalftoneError):
            HalftoneConfig(dot_size=-1)

    def test_angle_stored(self):
        cfg = HalftoneConfig(angle=30.0)
        assert cfg.angle == 30.0

    def test_angle_zero_valid(self):
        cfg = HalftoneConfig(angle=0.0)
        assert cfg.angle == 0.0

    def test_angle_359_valid(self):
        cfg = HalftoneConfig(angle=359.9)
        assert cfg.angle == pytest.approx(359.9)

    def test_angle_360_raises(self):
        with pytest.raises(HalftoneError):
            HalftoneConfig(angle=360.0)

    def test_negative_angle_raises(self):
        with pytest.raises(HalftoneError):
            HalftoneConfig(angle=-1.0)

    def test_custom_colours_stored(self):
        cfg = HalftoneConfig(foreground="#ff0000", background="#0000ff")
        assert cfg.foreground == "#ff0000"
        assert cfg.background == "#0000ff"


class TestApplyHalftone:
    def test_returns_image(self):
        img = _solid()
        cfg = HalftoneConfig()
        result = apply_halftone(img, cfg)
        assert isinstance(result, Image.Image)

    def test_output_size_matches_input(self):
        img = _solid(size=32)
        cfg = HalftoneConfig(dot_size=4)
        result = apply_halftone(img, cfg)
        assert result.size == img.size

    def test_disabled_returns_same_object(self):
        img = _solid()
        cfg = HalftoneConfig(enabled=False)
        result = apply_halftone(img, cfg)
        assert result is img

    def test_output_is_rgb(self):
        img = _solid()
        cfg = HalftoneConfig()
        result = apply_halftone(img, cfg)
        assert result.mode == "RGB"

    def test_white_input_produces_mostly_background(self):
        img = Image.new("RGB", (64, 64), (255, 255, 255))
        cfg = HalftoneConfig(foreground="#000000", background="#ffffff")
        result = apply_halftone(img, cfg)
        pixels = list(result.getdata())
        white_count = sum(1 for p in pixels if p == (255, 255, 255))
        assert white_count > len(pixels) * 0.8


class TestHalftoneConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        for key in (
            "TILESTITCH_HALFTONE_ENABLED",
            "TILESTITCH_HALFTONE_DOT_SIZE",
            "TILESTITCH_HALFTONE_ANGLE",
            "TILESTITCH_HALFTONE_FG",
            "TILESTITCH_HALFTONE_BG",
        ):
            monkeypatch.delenv(key, raising=False)
        cfg = halftone_config_from_env()
        assert cfg.enabled is True
        assert cfg.dot_size == 6

    def test_env_dot_size(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_HALFTONE_DOT_SIZE", "12")
        cfg = halftone_config_from_env()
        assert cfg.dot_size == 12

    def test_env_disabled(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_HALFTONE_ENABLED", "false")
        cfg = halftone_config_from_env()
        assert cfg.enabled is False

    def test_invalid_dot_size_raises(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_HALFTONE_DOT_SIZE", "abc")
        with pytest.raises(HalftoneError):
            halftone_config_from_env()
