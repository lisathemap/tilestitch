"""Tests for tilestitch.tile_label."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_label import LabelConfig, label_tile, label_config_from_env


def _blank(size: int = 256) -> Image.Image:
    return Image.new("RGB", (size, size), color=(200, 200, 200))


# ---------------------------------------------------------------------------
# LabelConfig
# ---------------------------------------------------------------------------

class TestLabelConfig:
    def test_defaults(self):
        cfg = LabelConfig()
        assert cfg.enabled is False
        assert cfg.font_size == 12
        assert cfg.show_zoom is True
        assert cfg.show_coords is True

    def test_small_font_raises(self):
        with pytest.raises(ValueError):
            LabelConfig(font_size=4)

    def test_minimum_font_size_ok(self):
        cfg = LabelConfig(font_size=6)
        assert cfg.font_size == 6


# ---------------------------------------------------------------------------
# label_tile
# ---------------------------------------------------------------------------

class TestLabelTile:
    def test_returns_image(self):
        cfg = LabelConfig(enabled=True)
        result = label_tile(_blank(), x=10, y=20, zoom=5, config=cfg)
        assert isinstance(result, Image.Image)

    def test_same_size_as_input(self):
        cfg = LabelConfig(enabled=True)
        img = _blank(256)
        result = label_tile(img, x=0, y=0, zoom=1, config=cfg)
        assert result.size == img.size

    def test_disabled_returns_original_unchanged(self):
        cfg = LabelConfig(enabled=False)
        img = _blank()
        result = label_tile(img, x=5, y=5, zoom=3, config=cfg)
        assert list(result.getdata()) == list(img.getdata())

    def test_does_not_mutate_input(self):
        cfg = LabelConfig(enabled=True)
        img = _blank()
        original_data = list(img.getdata())
        label_tile(img, x=1, y=2, zoom=4, config=cfg)
        assert list(img.getdata()) == original_data

    def test_output_is_rgb(self):
        cfg = LabelConfig(enabled=True)
        result = label_tile(_blank(), x=0, y=0, zoom=0, config=cfg)
        assert result.mode == "RGB"


# ---------------------------------------------------------------------------
# label_config_from_env
# ---------------------------------------------------------------------------

class TestLabelConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        for key in ("TILESTITCH_LABEL_TILES", "TILESTITCH_LABEL_FONT_SIZE",
                    "TILESTITCH_LABEL_SHOW_ZOOM", "TILESTITCH_LABEL_SHOW_COORDS"):
            monkeypatch.delenv(key, raising=False)
        cfg = label_config_from_env()
        assert cfg.enabled is False
        assert cfg.font_size == 12

    def test_enabled_via_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_LABEL_TILES", "1")
        cfg = label_config_from_env()
        assert cfg.enabled is True

    def test_font_size_via_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_LABEL_FONT_SIZE", "18")
        cfg = label_config_from_env()
        assert cfg.font_size == 18

    def test_show_zoom_disabled_via_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_LABEL_SHOW_ZOOM", "0")
        cfg = label_config_from_env()
        assert cfg.show_zoom is False
