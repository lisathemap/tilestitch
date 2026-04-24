"""Tests for tilestitch.tile_duotone and tilestitch.duotone_pipeline."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_duotone import (
    DuotoneConfig,
    DuotoneError,
    apply_duotone,
    duotone_config_from_env,
)
from tilestitch.duotone_pipeline import DuotoneStage, build_duotone_stage


def _solid(colour: tuple, mode: str = "RGB", size: tuple = (4, 4)) -> Image.Image:
    img = Image.new(mode, size, colour)
    return img


# ---------------------------------------------------------------------------
# DuotoneConfig
# ---------------------------------------------------------------------------

class TestDuotoneConfig:
    def test_defaults(self):
        cfg = DuotoneConfig()
        assert cfg.shadow == "000000"
        assert cfg.highlight == "ffffff"
        assert cfg.enabled is True

    def test_shadow_rgb_property(self):
        cfg = DuotoneConfig(shadow="ff0000")
        assert cfg.shadow_rgb == (255, 0, 0)

    def test_highlight_rgb_property(self):
        cfg = DuotoneConfig(highlight="0000ff")
        assert cfg.highlight_rgb == (0, 0, 255)

    def test_invalid_shadow_raises(self):
        with pytest.raises(DuotoneError):
            DuotoneConfig(shadow="zzzzzz")

    def test_invalid_highlight_raises(self):
        with pytest.raises(DuotoneError):
            DuotoneConfig(highlight="12345")

    def test_hash_prefix_stripped(self):
        cfg = DuotoneConfig(shadow="#aabbcc")
        assert cfg.shadow_rgb == (0xAA, 0xBB, 0xCC)


# ---------------------------------------------------------------------------
# apply_duotone
# ---------------------------------------------------------------------------

class TestApplyDuotone:
    def test_returns_image(self):
        cfg = DuotoneConfig(shadow="000000", highlight="ffffff")
        img = _solid((128, 128, 128))
        result = apply_duotone(img, cfg)
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self):
        cfg = DuotoneConfig()
        img = _solid((100, 150, 200), size=(8, 6))
        result = apply_duotone(img, cfg)
        assert result.size == (8, 6)

    def test_black_input_maps_to_shadow(self):
        cfg = DuotoneConfig(shadow="ff0000", highlight="0000ff")
        img = _solid((0, 0, 0))
        result = apply_duotone(img, cfg)
        r, g, b = result.getpixel((0, 0))[:3]
        assert r > 200
        assert g < 10
        assert b < 10

    def test_white_input_maps_to_highlight(self):
        cfg = DuotoneConfig(shadow="ff0000", highlight="00ff00")
        img = _solid((255, 255, 255))
        result = apply_duotone(img, cfg)
        r, g, b = result.getpixel((0, 0))[:3]
        assert r < 10
        assert g > 200

    def test_rgba_alpha_preserved(self):
        cfg = DuotoneConfig()
        img = _solid((100, 100, 100, 128), mode="RGBA")
        result = apply_duotone(img, cfg)
        assert result.mode == "RGBA"
        assert result.getpixel((0, 0))[3] == 128


# ---------------------------------------------------------------------------
# DuotoneStage / build_duotone_stage
# ---------------------------------------------------------------------------

class TestDuotoneStage:
    def test_returns_same_image_when_config_none(self):
        stage = DuotoneStage(config=None)
        img = _solid((10, 20, 30))
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        cfg = DuotoneConfig(enabled=False)
        stage = DuotoneStage(config=cfg)
        img = _solid((10, 20, 30))
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        cfg = DuotoneConfig(shadow="003366", highlight="ffcc00")
        stage = DuotoneStage(config=cfg)
        img = _solid((80, 80, 80))
        result = stage.process(img)
        assert isinstance(result, Image.Image)
        assert result is not img

    def test_build_duotone_stage_returns_stage(self):
        cfg = DuotoneConfig()
        stage = build_duotone_stage(config=cfg)
        assert isinstance(stage, DuotoneStage)

    def test_build_duotone_stage_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_DUOTONE_SHADOW", "112233")
        monkeypatch.setenv("TILESTITCH_DUOTONE_HIGHLIGHT", "aabbcc")
        monkeypatch.setenv("TILESTITCH_DUOTONE_ENABLED", "true")
        stage = build_duotone_stage()
        assert stage.config.shadow == "112233"
        assert stage.config.highlight == "aabbcc"
        assert stage.config.enabled is True
