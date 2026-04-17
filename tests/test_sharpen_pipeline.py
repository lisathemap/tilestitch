"""Tests for tilestitch.sharpen_pipeline."""

from PIL import Image

from tilestitch.tile_sharpen import SharpenConfig
from tilestitch.sharpen_pipeline import SharpenStage, build_sharpen_stage


def _blank(size: int = 64) -> Image.Image:
    return Image.new("RGB", (size, size), (100, 100, 100))


class TestSharpenStage:
    def test_returns_same_image_when_disabled(self):
        img = _blank()
        stage = SharpenStage(config=SharpenConfig(enabled=False, factor=2.0))
        assert stage.process(img) is img

    def test_returns_same_image_when_config_none(self):
        img = _blank()
        stage = SharpenStage(config=None)
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        img = _blank()
        stage = SharpenStage(config=SharpenConfig(enabled=True, factor=2.0))
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_output_size_preserved(self):
        img = _blank(size=128)
        stage = SharpenStage(config=SharpenConfig(enabled=True, factor=2.0))
        result = stage.process(img)
        assert result.size == (128, 128)

    def test_build_sharpen_stage_returns_stage(self):
        cfg = SharpenConfig(enabled=False)
        stage = build_sharpen_stage(cfg)
        assert isinstance(stage, SharpenStage)
        assert stage.config is cfg
