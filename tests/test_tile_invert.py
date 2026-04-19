"""Tests for tilestitch.tile_invert."""
from __future__ import annotations

import os
import pytest
from PIL import Image

from tilestitch.tile_invert import (
    InvertConfig,
    InvertError,
    apply_invert,
    invert_config_from_env,
)


def _solid(colour: tuple, mode: str = "RGB", size: tuple = (4, 4)) -> Image.Image:
    img = Image.new(mode, size, colour)
    return img


class TestInvertConfig:
    def test_defaults(self):
        cfg = InvertConfig()
        assert cfg.enabled is False
        assert cfg.preserve_alpha is True

    def test_enabled_stored(self):
        cfg = InvertConfig(enabled=True)
        assert cfg.enabled is True

    def test_invalid_enabled_raises(self):
        with pytest.raises(InvertError):
            InvertConfig(enabled="yes")  # type: ignore

    def test_invalid_preserve_alpha_raises(self):
        with pytest.raises(InvertError):
            InvertConfig(preserve_alpha=1)  # type: ignore


class TestApplyInvert:
    def test_disabled_returns_same_image(self):
        img = _solid((100, 150, 200))
        cfg = InvertConfig(enabled=False)
        result = apply_invert(img, cfg)
        assert result is img

    def test_rgb_inversion(self):
        img = _solid((0, 0, 0))
        cfg = InvertConfig(enabled=True)
        result = apply_invert(img, cfg)
        px = result.getpixel((0, 0))
        assert px == (255, 255, 255)

    def test_rgb_partial_inversion(self):
        img = _solid((100, 150, 200))
        cfg = InvertConfig(enabled=True)
        result = apply_invert(img, cfg)
        px = result.getpixel((0, 0))
        assert px == (155, 105, 55)

    def test_rgba_preserves_alpha(self):
        img = _solid((80, 80, 80, 128), mode="RGBA")
        cfg = InvertConfig(enabled=True, preserve_alpha=True)
        result = apply_invert(img, cfg)
        assert result.mode == "RGBA"
        px = result.getpixel((0, 0))
        assert px[3] == 128
        assert px[0] == 175

    def test_rgba_without_preserve_alpha_converts(self):
        img = _solid((80, 80, 80, 255), mode="RGBA")
        cfg = InvertConfig(enabled=True, preserve_alpha=False)
        result = apply_invert(img, cfg)
        assert result.mode == "RGB"


class TestInvertConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_INVERT_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_INVERT_PRESERVE_ALPHA", raising=False)
        cfg = invert_config_from_env()
        assert cfg.enabled is False
        assert cfg.preserve_alpha is True

    def test_enabled_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_INVERT_ENABLED", "true")
        cfg = invert_config_from_env()
        assert cfg.enabled is True

    def test_preserve_alpha_false_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_INVERT_PRESERVE_ALPHA", "false")
        cfg = invert_config_from_env()
        assert cfg.preserve_alpha is False
