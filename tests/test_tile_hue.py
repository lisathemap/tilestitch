from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_hue import HueConfig, HueError, apply_hue
from tilestitch.hue_pipeline import HueStage, build_hue_stage


def _solid(colour: tuple[int, int, int] = (100, 150, 200)) -> Image.Image:
    img = Image.new("RGB", (64, 64), colour)
    return img


class TestHueConfig:
    def test_defaults(self):
        cfg = HueConfig()
        assert cfg.enabled is True
        assert cfg.factor == 1.0

    def test_factor_stored(self):
        cfg = HueConfig(factor=0.5)
        assert cfg.factor == 0.5

    def test_zero_factor_valid(self):
        cfg = HueConfig(factor=0.0)
        assert cfg.factor == 0.0

    def test_negative_factor_raises(self):
        with pytest.raises(HueError):
            HueConfig(factor=-0.1)

    def test_factor_above_one_valid(self):
        cfg = HueConfig(factor=2.5)
        assert cfg.factor == 2.5


class TestApplyHue:
    def test_returns_image(self):
        img = _solid()
        result = apply_hue(img, HueConfig())
        assert isinstance(result, Image.Image)

    def test_factor_one_returns_same_object(self):
        img = _solid()
        result = apply_hue(img, H))
        assert result is img

    def test_disabled_returns_same_object(self):
        img = _solid()
        result = apply_hue(img, HueConfig(enabled=False, factor=0.0))
        assert result is img

    def test_zero_factor_produces_grayscale_like_result(self):
        img = _solid((100, 150, 200))
        result = apply_hue(img, HueConfig(factor=0.0))
        px = result.getpixel((0, 0))
        # All channels should be equal (grayscale)
        assert px[0] == px[1] == px[2]

    def test_output_size_unchanged(self):
        img = _solid()
        result = apply_hue(img, HueConfig(factor=0.5))
        assert result.size == img.size


class TestHueStage:
    def test_returns_same_image_when_config_none(self):
        stage = HueStage(config=None)
        img = _solid()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        stage = HueStage(config=HueConfig(factor=0.5))
        img = _solid()
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_build_hue_stage_returns_stage(self):
        stage = build_hue_stage(HueConfig(factor=1.5))
        assert isinstance(stage, HueStage)
        assert stage.config is not None
        assert stage.config.factor == 1.5

    def test_build_hue_stage_defaults(self):
        stage = build_hue_stage()
        assert stage.config.factor == 1.0
