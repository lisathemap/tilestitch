"""Tests for tile_solarize and solarize_pipeline."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_solarize import (
    SolarizeConfig,
    SolarizeError,
    apply_solarize,
    solarize_config_from_env,
)
from tilestitch.solarize_pipeline import SolarizeStage, build_solarize_stage


def _solid(colour: tuple, mode: str = "RGB", size: tuple = (4, 4)) -> Image.Image:
    img = Image.new(mode, size, colour)
    return img


class TestSolarizeConfig:
    def test_defaults(self):
        cfg = SolarizeConfig()
        assert cfg.enabled is True
        assert cfg.threshold == 128

    def test_threshold_stored(self):
        cfg = SolarizeConfig(threshold=200)
        assert cfg.threshold == 200

    def test_threshold_zero_valid(self):
        cfg = SolarizeConfig(threshold=0)
        assert cfg.threshold == 0

    def test_threshold_255_valid(self):
        cfg = SolarizeConfig(threshold=255)
        assert cfg.threshold == 255

    def test_threshold_below_zero_raises(self):
        with pytest.raises(SolarizeError):
            SolarizeConfig(threshold=-1)

    def test_threshold_above_255_raises(self):
        with pytest.raises(SolarizeError):
            SolarizeConfig(threshold=256)

    def test_invalid_enabled_raises(self):
        with pytest.raises(SolarizeError):
            SolarizeConfig(enabled="yes")  # type: ignore


class TestApplySolarize:
    def test_returns_image(self):
        img = _solid((200, 200, 200))
        cfg = SolarizeConfig(enabled=True, threshold=128)
        result = apply_solarize(img, cfg)
        assert isinstance(result, Image.Image)

    def test_disabled_returns_same_object(self):
        img = _solid((200, 200, 200))
        cfg = SolarizeConfig(enabled=False)
        result = apply_solarize(img, cfg)
        assert result is img

    def test_pixels_above_threshold_inverted(self):
        img = _solid((200, 200, 200))
        cfg = SolarizeConfig(enabled=True, threshold=128)
        result = apply_solarize(img, cfg)
        px = result.getpixel((0, 0))
        assert px == (55, 55, 55)

    def test_pixels_below_threshold_unchanged(self):
        img = _solid((50, 50, 50))
        cfg = SolarizeConfig(enabled=True, threshold=128)
        result = apply_solarize(img, cfg)
        px = result.getpixel((0, 0))
        assert px == (50, 50, 50)

    def test_rgba_alpha_preserved(self):
        img = _solid((200, 200, 200, 100), mode="RGBA")
        cfg = SolarizeConfig(enabled=True, threshold=128)
        result = apply_solarize(img, cfg)
        assert result.mode == "RGBA"
        assert result.getpixel((0, 0))[3] == 100


class TestSolarizeStage:
    def test_returns_same_image_when_config_none(self):
        img = _solid((100, 100, 100))
        stage = SolarizeStage(config=None)
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        img = _solid((100, 100, 100))
        stage = SolarizeStage(config=SolarizeConfig(enabled=False))
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        img = _solid((200, 200, 200))
        stage = SolarizeStage(config=SolarizeConfig(enabled=True, threshold=128))
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_build_solarize_stage_returns_stage(self):
        stage = build_solarize_stage(SolarizeConfig(enabled=False))
        assert isinstance(stage, SolarizeStage)

    def test_build_solarize_stage_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SOLARIZE_ENABLED", "false")
        monkeypatch.setenv("TILESTITCH_SOLARIZE_THRESHOLD", "100")
        stage = build_solarize_stage()
        assert stage.config.threshold == 100
        assert stage.config.enabled is False
