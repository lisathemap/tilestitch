"""Tests for tilestitch.tile_chroma."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_chroma import (
    ChromaConfig,
    ChromaError,
    apply_chroma,
    chroma_config_from_env,
)


def _solid(colour: tuple, size: tuple = (4, 4)) -> Image.Image:
    img = Image.new("RGB", size, colour)
    return img


class TestChromaConfig:
    def test_defaults(self):
        cfg = ChromaConfig()
        assert cfg.key_colour == "#00ff00"
        assert cfg.replacement_colour == "#ffffff"
        assert cfg.threshold == 30
        assert cfg.enabled is True

    def test_key_rgb_property(self):
        cfg = ChromaConfig(key_colour="#ff0000")
        assert cfg.key_rgb == (255, 0, 0)

    def test_replacement_rgb_property(self):
        cfg = ChromaConfig(replacement_colour="#0000ff")
        assert cfg.replacement_rgb == (0, 0, 255)

    def test_invalid_key_colour_raises(self):
        with pytest.raises(ChromaError):
            ChromaConfig(key_colour="#gg0000")

    def test_invalid_replacement_colour_raises(self):
        with pytest.raises(ChromaError):
            ChromaConfig(replacement_colour="short")

    def test_negative_threshold_raises(self):
        with pytest.raises(ChromaError):
            ChromaConfig(threshold=-1)

    def test_threshold_above_255_raises(self):
        with pytest.raises(ChromaError):
            ChromaConfig(threshold=256)

    def test_threshold_zero_valid(self):
        cfg = ChromaConfig(threshold=0)
        assert cfg.threshold == 0

    def test_threshold_255_valid(self):
        cfg = ChromaConfig(threshold=255)
        assert cfg.threshold == 255


class TestApplyChroma:
    def test_replaces_exact_key_colour(self):
        img = _solid((0, 255, 0))
        cfg = ChromaConfig(key_colour="#00ff00", replacement_colour="#ff0000", threshold=0)
        result = apply_chroma(img, cfg)
        px = result.getpixel((0, 0))
        assert px[:3] == (255, 0, 0)

    def test_does_not_replace_non_matching_pixel(self):
        img = _solid((255, 0, 0))
        cfg = ChromaConfig(key_colour="#00ff00", replacement_colour="#0000ff", threshold=0)
        result = apply_chroma(img, cfg)
        px = result.getpixel((0, 0))
        assert px[:3] == (255, 0, 0)

    def test_threshold_allows_nearby_colours(self):
        img = _solid((10, 245, 10))
        cfg = ChromaConfig(key_colour="#00ff00", replacement_colour="#ffffff", threshold=20)
        result = apply_chroma(img, cfg)
        px = result.getpixel((0, 0))
        assert px[:3] == (255, 255, 255)

    def test_disabled_returns_original(self):
        img = _solid((0, 255, 0))
        cfg = ChromaConfig(enabled=False)
        result = apply_chroma(img, cfg)
        assert result is img

    def test_output_is_rgba(self):
        img = _solid((0, 255, 0))
        cfg = ChromaConfig()
        result = apply_chroma(img, cfg)
        assert result.mode == "RGBA"


class TestChromaConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        for key in (
            "TILESTITCH_CHROMA_KEY",
            "TILESTITCH_CHROMA_REPLACEMENT",
            "TILESTITCH_CHROMA_THRESHOLD",
            "TILESTITCH_CHROMA_ENABLED",
        ):
            monkeypatch.delenv(key, raising=False)
        cfg = chroma_config_from_env()
        assert cfg.key_colour == "#00ff00"
        assert cfg.threshold == 30
        assert cfg.enabled is True

    def test_reads_env_values(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_CHROMA_KEY", "#ff00ff")
        monkeypatch.setenv("TILESTITCH_CHROMA_THRESHOLD", "15")
        monkeypatch.setenv("TILESTITCH_CHROMA_ENABLED", "false")
        monkeypatch.delenv("TILESTITCH_CHROMA_REPLACEMENT", raising=False)
        cfg = chroma_config_from_env()
        assert cfg.key_colour == "#ff00ff"
        assert cfg.threshold == 15
        assert cfg.enabled is False
