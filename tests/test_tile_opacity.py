import pytest
from PIL import Image

from tilestitch.tile_opacity import (
    OpacityConfig,
    OpacityError,
    apply_opacity,
    opacity_config_from_env,
)
from tilestitch.opacity_pipeline import OpacityStage, build_opacity_stage


def _solid(colour=(255, 0, 0, 255), size=(4, 4)) -> Image.Image:
    img = Image.new("RGBA", size, colour)
    return img


class TestOpacityConfig:
    def test_defaults(self):
        cfg = OpacityConfig()
        assert cfg.enabled is True
        assert cfg.alpha == 1.0

    def test_alpha_stored(self):
        cfg = OpacityConfig(alpha=0.5)
        assert cfg.alpha == 0.5

    def test_alpha_zero_valid(self):
        cfg = OpacityConfig(alpha=0.0)
        assert cfg.alpha == 0.0

    def test_alpha_one_valid(self):
        cfg = OpacityConfig(alpha=1.0)
        assert cfg.alpha == 1.0

    def test_alpha_above_one_raises(self):
        with pytest.raises(OpacityError):
            OpacityConfig(alpha=1.1)

    def test_negative_alpha_raises(self):
        with pytest.raises(OpacityError):
            OpacityConfig(alpha=-0.1)


class TestApplyOpacity:
    def test_full_opacity_returns_unchanged_pixels(self):
        img = _solid((255, 0, 0, 255))
        result = apply_opacity(img, OpacityConfig(alpha=1.0))
        assert result.getpixel((0, 0))[3] == 255

    def test_half_opacity_halves_alpha(self):
        img = _solid((255, 0, 0, 255))
        result = apply_opacity(img, OpacityConfig(alpha=0.5))
        assert result.getpixel((0, 0))[3] == 127

    def test_zero_opacity_makes_transparent(self):
        img = _solid((255, 0, 0, 255))
        result = apply_opacity(img, OpacityConfig(alpha=0.0))
        assert result.getpixel((0, 0))[3] == 0

    def test_disabled_returns_original(self):
        img = _solid((255, 0, 0, 255))
        cfg = OpacityConfig(enabled=False, alpha=0.0)
        result = apply_opacity(img, cfg)
        assert result is img

    def test_rgb_image_converted_to_rgba(self):
        img = Image.new("RGB", (4, 4), (100, 100, 100))
        result = apply_opacity(img, OpacityConfig(alpha=0.5))
        assert result.mode == "RGBA"


class TestOpacityStage:
    def test_returns_image_when_enabled(self):
        stage = build_opacity_stage(OpacityConfig(alpha=0.5))
        img = _solid()
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_returns_same_image_when_disabled(self):
        stage = OpacityStage(config=OpacityConfig(enabled=False, alpha=0.5))
        img = _solid()
        assert stage.process(img) is img

    def test_returns_same_image_when_config_none(self):
        stage = OpacityStage(config=None)
        img = _solid()
        assert stage.process(img) is img

    def test_build_opacity_stage_defaults(self):
        stage = build_opacity_stage()
        assert stage.config is not None
        assert stage.config.alpha == 1.0
