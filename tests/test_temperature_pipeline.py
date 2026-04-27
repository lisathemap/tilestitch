"""Tests for tilestitch.temperature_pipeline."""
from __future__ import annotations

from PIL import Image

from tilestitch.tile_temperature import TemperatureConfig
from tilestitch.temperature_pipeline import TemperatureStage, build_temperature_stage


def _blank(size: int = 8) -> Image.Image:
    return Image.new("RGB", (size, size), (120, 120, 120))


class TestTemperatureStage:
    def test_returns_same_image_when_config_none(self):
        stage = TemperatureStage(None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        cfg = TemperatureConfig(enabled=False, shift=0.8)
        stage = TemperatureStage(cfg)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        cfg = TemperatureConfig(enabled=True, shift=0.5)
        stage = TemperatureStage(cfg)
        img = _blank()
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_warm_shift_changes_pixels(self):
        cfg = TemperatureConfig(enabled=True, shift=1.0)
        stage = TemperatureStage(cfg)
        img = Image.new("RGB", (4, 4), (100, 100, 200))
        result = stage.process(img)
        before = img.getpixel((0, 0))
        after = result.getpixel((0, 0))
        assert after != before

    def test_build_temperature_stage_returns_stage(self):
        cfg = TemperatureConfig(enabled=False)
        stage = build_temperature_stage(cfg)
        assert isinstance(stage, TemperatureStage)

    def test_build_temperature_stage_no_args_uses_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_TEMPERATURE_ENABLED", "false")
        monkeypatch.setenv("TILESTITCH_TEMPERATURE_SHIFT", "0")
        stage = build_temperature_stage()
        assert isinstance(stage, TemperatureStage)
