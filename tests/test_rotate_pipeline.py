import pytest
from PIL import Image

from tilestitch.tile_rotate import RotateConfig
from tilestitch.rotate_pipeline import RotateStage, build_rotate_stage


def _blank(size: int = 64) -> Image.Image:
    return Image.new("RGB", (size, size), "white")


class TestRotateStage:
    def test_returns_same_image_when_config_none(self):
        stage = RotateStage(config=None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_angle_zero(self):
        stage = RotateStage(config=RotateConfig(angle=0.0))
        img = _blank()
        assert stage.process(img) is img

    def test_returns_rotated_image(self):
        stage = RotateStage(config=RotateConfig(angle=90.0, expand=True))
        img = Image.new("RGB", (100, 50), "red")
        result = stage.process(img)
        assert result.size == (50, 100)

    def test_build_rotate_stage_returns_stage(self):
        stage = build_rotate_stage(RotateConfig(angle=0.0))
        assert isinstance(stage, RotateStage)

    def test_build_rotate_stage_uses_provided_config(self):
        cfg = RotateConfig(angle=45.0)
        stage = build_rotate_stage(cfg)
        assert stage.config.angle == 45.0
