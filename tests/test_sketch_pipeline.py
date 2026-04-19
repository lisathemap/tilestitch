"""Tests for tilestitch.sketch_pipeline."""
import pytest
from PIL import Image

from tilestitch.tile_sketch import SketchConfig
from tilestitch.sketch_pipeline import SketchStage, build_sketch_stage


def _blank(size=(64, 64)) -> Image.Image:
    return Image.new("RGB", size, (180, 160, 140))


class TestSketchStage:
    def test_returns_same_image_when_config_none(self):
        stage = SketchStage(config=None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        stage = SketchStage(config=SketchConfig(enabled=False))
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        stage = SketchStage(config=SketchConfig(enabled=True, blend=0.5))
        img = _blank()
        result = stage.process(img)
        assert isinstance(result, Image.Image)
        assert result.size == img.size

    def test_build_sketch_stage_returns_stage(self):
        stage = build_sketch_stage(SketchConfig())
        assert isinstance(stage, SketchStage)

    def test_build_sketch_stage_uses_provided_config(self):
        cfg = SketchConfig(blend=0.3)
        stage = build_sketch_stage(cfg)
        assert stage.config is cfg
