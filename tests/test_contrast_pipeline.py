import pytest
from PIL import Image

from tilestitch.tile_contrast import ContrastConfig
from tilestitch.contrast_pipeline import ContrastStage, build_contrast_stage


def _blank() -> Image.Image:
    return Image.new("RGB", (8, 8), (100, 100, 100))


class TestContrastStage:
    def test_returns_image_when_enabled(self):
        cfg = ContrastConfig(enabled=True, factor=1.5)
        stage = ContrastStage(config=cfg)
        result = stage.process(_blank())
        assert isinstance(result, Image.Image)

    def test_returns_same_image_when_disabled(self):
        img = _blank()
        cfg = ContrastConfig(enabled=False, factor=2.0)
        stage = ContrastStage(config=cfg)
        assert stage.process(img) is img

    def test_returns_same_image_when_config_none(self):
        img = _blank()
        stage = ContrastStage(config=None)
        assert stage.process(img) is img

    def test_build_contrast_stage_default(self):
        stage = build_contrast_stage()
        assert isinstance(stage, ContrastStage)
        assert stage.config is not None

    def test_build_contrast_stage_custom(self):
        cfg = ContrastConfig(enabled=True, factor=0.5)
        stage = build_contrast_stage(cfg)
        assert stage.config.factor == pytest.approx(0.5)
