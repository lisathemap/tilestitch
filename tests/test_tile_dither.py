"""Tests for tilestitch.tile_dither."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_dither import (
    DitherConfig,
    DitherError,
    apply_dither,
    dither_config_from_env,
)


def _solid(colour: tuple[int, int, int] = (100, 150, 200), size: int = 64) -> Image.Image:
    img = Image.new("RGB", (size, size), colour)
    return img


class TestDitherConfig:
    def test_defaults(self):
        cfg = DitherConfig()
        assert cfg.enabled is False
        assert cfg.mode == "floydsteinberg"
        assert cfg.colours == 256

    def test_mode_normalised_to_lowercase(self):
        cfg = DitherConfig(mode="FloydSteinberg")
        assert cfg.mode == "floydsteinberg"

    def test_whitespace_stripped_from_mode(self):
        cfg = DitherConfig(mode="  ordered  ")
        assert cfg.mode == "ordered"

    def test_invalid_mode_raises(self):
        with pytest.raises(DitherError, match="Invalid dither mode"):
            DitherConfig(mode="halftone")

    def test_none_mode_valid(self):
        cfg = DitherConfig(mode="none")
        assert cfg.mode == "none"

    def test_colours_minimum_valid(self):
        cfg = DitherConfig(colours=2)
        assert cfg.colours == 2

    def test_colours_maximum_valid(self):
        cfg = DitherConfig(colours=256)
        assert cfg.colours == 256

    def test_one_colour_raises(self):
        with pytest.raises(DitherError, match="colours must be between"):
            DitherConfig(colours=1)

    def test_too_many_colours_raises(self):
        with pytest.raises(DitherError, match="colours must be between"):
            DitherConfig(colours=257)


class TestApplyDither:
    def test_returns_image_when_disabled(self):
        img = _solid()
        cfg = DitherConfig(enabled=False)
        result = apply_dither(img, cfg)
        assert result is img

    def test_returns_image_when_mode_none(self):
        img = _solid()
        cfg = DitherConfig(enabled=True, mode="none")
        result = apply_dither(img, cfg)
        assert result is img

    def test_returns_image_instance_when_enabled(self):
        img = _solid()
        cfg = DitherConfig(enabled=True, mode="floydsteinberg", colours=64)
        result = apply_dither(img, cfg)
        assert isinstance(result, Image.Image)

    def test_output_mode_preserved_floydsteinberg(self):
        img = _solid()
        cfg = DitherConfig(enabled=True, mode="floydsteinberg", colours=128)
        result = apply_dither(img, cfg)
        assert result.mode == "RGB"

    def test_output_mode_preserved_ordered(self):
        img = _solid()
        cfg = DitherConfig(enabled=True, mode="ordered", colours=32)
        result = apply_dither(img, cfg)
        assert result.mode == "RGB"

    def test_output_size_unchanged(self):
        img = _solid(size=64)
        cfg = DitherConfig(enabled=True, mode="floydsteinberg")
        result = apply_dither(img, cfg)
        assert result.size == (64, 64)


class TestDitherConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        for key in ("TILESTITCH_DITHER_ENABLED", "TILESTITCH_DITHER_MODE", "TILESTITCH_DITHER_COLOURS"):
            monkeypatch.delenv(key, raising=False)
        cfg = dither_config_from_env()
        assert cfg.enabled is False
        assert cfg.mode == "floydsteinberg"
        assert cfg.colours == 256

    def test_enabled_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_DITHER_ENABLED", "true")
        cfg = dither_config_from_env()
        assert cfg.enabled is True

    def test_mode_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_DITHER_MODE", "ordered")
        cfg = dither_config_from_env()
        assert cfg.mode == "ordered"

    def test_colours_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_DITHER_COLOURS", "16")
        cfg = dither_config_from_env()
        assert cfg.colours == 16
