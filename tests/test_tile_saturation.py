from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_saturation import (
    SaturationConfig,
    SaturationError,
    apply_saturation,
    saturation_config_from_env,
)
from tilestitch.saturation_pipeline import SaturationStage, build_saturation_stage


def _solid(colour: tuple[int, int, int] = (100, 150, 200)) -> Image.Image:
    img = Image.new("RGB", (4, 4), colour)
    return img


class TestSaturationConfig:
    def test_defaults(self):
        cfg = SaturationConfig()
        assert cfg.factor == 1.0
        assert cfg.enabled is True

    def test_factor_stored(self):
        cfg = SaturationConfig(factor=2.0)
        assert cfg.factor == 2.0

    def test_zero_factor_valid(self):
        cfg = SaturationConfig(factor=0.0)
        assert cfg.factor == 0.0

    def test_negative_factor_raises(self):
        with pytest.raises(SaturationError):
            SaturationConfig(factor=-0.1)

    def test_enabled_false_stored(self):
        cfg = SaturationConfig(enabled=False)
        assert cfg.enabled is False


class TestApplySaturation:
    def test_returns_image(self):
        img = _solid()
        cfg = SaturationConfig(factor=1.5)
        result = apply_saturation(img, cfg)
        assert isinstance(result, Image.Image)

    def test_disabled_returns_same_object(self):
        img = _solid()
        cfg = SaturationConfig(enabled=False)
        result = apply_saturation(img, cfg)
        assert result is img

    def test_zero_factor_produces_grayscale_like(self):
        img = _solid((100, 150, 200))
        cfg = SaturationConfig(factor=0.0)
        result = apply_saturation(img, cfg)
        px = result.getpixel((0, 0))
        assert px[0] == px[1] == px[2]

    def test_size_preserved(self):
        img = _solid()
        cfg = SaturationConfig(factor=2.0)
        result = apply_saturation(img, cfg)
        assert result.size == img.size


class TestSaturationConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_SATURATION_FACTOR", raising=False)
        monkeypatch.delenv("TILESTITCH_SATURATION_ENABLED", raising=False)
        cfg = saturation_config_from_env()
        assert cfg.factor == 1.0
        assert cfg.enabled is True

    def test_reads_factor_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SATURATION_FACTOR", "0.5")
        cfg = saturation_config_from_env()
        assert cfg.factor == 0.5

    def test_reads_enabled_false_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SATURATION_ENABLED", "false")
        cfg = saturation_config_from_env()
        assert cfg.enabled is False

    def test_invalid_enabled_raises(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SATURATION_ENABLED", "maybe")
        with pytest.raises(SaturationError):
            saturation_config_from_env()


class TestSaturationStage:
    def test_returns_same_image_when_config_none(self):
        img = _solid()
        stage = build_saturation_stage(None)
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        img = _solid()
        stage = build_saturation_stage(SaturationConfig(enabled=False))
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        img = _solid()
        stage = build_saturation_stage(SaturationConfig(factor=1.5))
        result = stage.process(img)
        assert isinstance(result, Image.Image)
