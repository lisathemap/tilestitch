"""Tests for mosaic_pipeline."""
from PIL import Image

from tilestitch.tile_mosaic import MosaicConfig
from tilestitch.mosaic_pipeline import MosaicStage, build_mosaic_stage


def _blank(size=(64, 64)) -> Image.Image:
    return Image.new("RGBA", size, (128, 128, 128, 255))


class TestMosaicStage:
    def test_returns_same_image_when_config_none(self):
        stage = MosaicStage(config=None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        stage = MosaicStage(config=MosaicConfig(enabled=False))
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        stage = MosaicStage(config=MosaicConfig(enabled=True, tile_size=8))
        img = _blank()
        result = stage.process(img)
        assert isinstance(result, Image.Image)
        assert result.size == img.size

    def test_build_mosaic_stage_returns_stage(self):
        stage = build_mosaic_stage(MosaicConfig(enabled=True, tile_size=16))
        assert isinstance(stage, MosaicStage)

    def test_build_mosaic_stage_none_uses_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_MOSAIC_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_MOSAIC_TILE_SIZE", raising=False)
        stage = build_mosaic_stage()
        assert isinstance(stage, MosaicStage)
