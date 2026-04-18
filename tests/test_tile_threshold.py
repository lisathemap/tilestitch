"""Tests for tilestitch.tile_threshold and tilestitch.threshold_pipeline."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_threshold import (
    ThresholdConfig,
    ThresholdError,
    apply_threshold,
)
from tilestitch.threshold_pipeline import ThresholdStage, build_threshold_stage


def _solid(r: int, g: int, b: int, size: int = 4) -> Image.Image:
    img = Image.new("RGBA", (size, size), (r, g, b, 255))
    return img


# ---------------------------------------------------------------------------
# ThresholdConfig
# ---------------------------------------------------------------------------

class TestThresholdConfig:
    def test_defaults(self):
        cfg = ThresholdConfig()
        assert cfg.enabled is False
        assert cfg.level == 128

    def test_level_stored(self):
        cfg = ThresholdConfig(enabled=True, level=200)
        assert cfg.level == 200

    def test_level_zero_valid(self):
        cfg = ThresholdConfig(level=0)
        assert cfg.level == 0

    def test_level_255_valid(self):
        cfg = ThresholdConfig(level=255)
        assert cfg.level == 255

    def test_level_below_zero_raises(self):
        with pytest.raises(ThresholdError):
            ThresholdConfig(level=-1)

    def test_level_above_255_raises(self):
        with pytest.raises(ThresholdError):
            ThresholdConfig(level=256)

    def test_invalid_enabled_raises(self):
        with pytest.raises(ThresholdError):
            ThresholdConfig(enabled="yes")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# apply_threshold
# ---------------------------------------------------------------------------

class TestApplyThreshold:
    def test_disabled_returns_same_image(self):
        img = _solid(100, 100, 100)
        cfg = ThresholdConfig(enabled=False)
        result = apply_threshold(img, cfg)
        assert result is img

    def test_returns_rgba(self):
        img = _solid(200, 200, 200)
        cfg = ThresholdConfig(enabled=True, level=128)
        result = apply_threshold(img, cfg)
        assert result.mode == "RGBA"

    def test_bright_pixel_becomes_white(self):
        img = _solid(255, 255, 255)
        cfg = ThresholdConfig(enabled=True, level=128)
        result = apply_threshold(img, cfg)
        r, g, b, a = result.getpixel((0, 0))
        assert (r, g, b) == (255, 255, 255)

    def test_dark_pixel_becomes_black(self):
        img = _solid(10, 10, 10)
        cfg = ThresholdConfig(enabled=True, level=128)
        result = apply_threshold(img, cfg)
        r, g, b, a = result.getpixel((0, 0))
        assert (r, g, b) == (0, 0, 0)


# ---------------------------------------------------------------------------
# ThresholdStage / build_threshold_stage
# ---------------------------------------------------------------------------

class TestThresholdStage:
    def test_returns_same_image_when_disabled(self):
        img = _solid(128, 128, 128)
        stage = ThresholdStage(config=ThresholdConfig(enabled=False))
        assert stage.process(img) is img

    def test_returns_same_image_when_config_none(self):
        img = _solid(128, 128, 128)
        stage = ThresholdStage(config=None)
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        img = _solid(200, 200, 200)
        stage = ThresholdStage(config=ThresholdConfig(enabled=True, level=100))
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_build_creates_stage(self):
        stage = build_threshold_stage()
        assert isinstance(stage, ThresholdStage)
        assert stage.config is not None
