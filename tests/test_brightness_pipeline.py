"""Tests for tilestitch.brightness_pipeline."""
from PIL import Image

from tilestitch.tile_brightness import BrightnessConfig
from tilestitch.brightness_pipeline import BrightnessStage, build_brightness_stage


def _blank(size: int = 8) -> Image.Image:
    return Image.new("RGB", (size, size), (128, 128, 128))


class TestBrightnessStage:
    def test_returns_image_when_enabled(self):
        cfg = BrightnessConfig(brightness=1.5)
        stage = BrightnessStage(config=cfg, enabled=True)
        out = stage.process(_blank())
        assert isinstance(out, Image.Image)

    def test_returns_same_image_when_disabled(self):
        cfg = BrightnessConfig(brightness=2.0)
        stage = BrightnessStage(config=cfg, enabled=False)
        img = _blank()
        out = stage.process(img)
        assert out is img

    def test_returns_same_image_when_config_none(self):
        stage = BrightnessStage(config=None, enabled=True)
        img = _blank()
        out = stage.process(img)
        assert out is img

    def test_brightness_applied(self):
        cfg = BrightnessConfig(brightness=2.0, contrast=1.0)
        stage = BrightnessStage(config=cfg, enabled=True)
        img = _blank()
        out = stage.process(img)
        assert out.getpixel((0, 0))[0] > 128


class TestBuildBrightnessStage:
    def test_returns_brightness_stage(self):
        stage = build_brightness_stage()
        assert isinstance(stage, BrightnessStage)

    def test_disabled_by_default_false(self):
        stage = build_brightness_stage(enabled=True)
        assert stage.enabled is True

    def test_config_stored(self):
        cfg = BrightnessConfig(brightness=1.2)
        stage = build_brightness_stage(config=cfg)
        assert stage.config is cfg
