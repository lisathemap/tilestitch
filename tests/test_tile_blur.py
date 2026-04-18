import pytest
from PIL import Image

from tilestitch.tile_blur import BlurConfig, BlurError, apply_blur
from tilestitch.blur_pipeline import BlurStage, build_blur_stage


def _solid(colour: tuple = (100, 150, 200), size: tuple = (64, 64)) -> Image.Image:
    img = Image.new("RGB", size, colour)
    return img


class TestBlurConfig:
    def test_defaults(self):
        cfg = BlurConfig()
        assert cfg.enabled is False
        assert cfg.radius == 1.0

    def test_radius_stored(self):
        cfg = BlurConfig(radius=3.5)
        assert cfg.radius == 3.5

    def test_zero_radius_raises(self):
        with pytest.raises(BlurError):
            BlurConfig(radius=0)

    def test_negative_radius_raises(self):
        with pytest.raises(BlurError):
            BlurConfig(radius=-1.0)

    def test_enabled_stored(self):
        cfg = BlurConfig(enabled=True)
        assert cfg.enabled is True


class TestApplyBlur:
    def test_returns_image_when_disabled(self):
        img = _solid()
        cfg = BlurConfig(enabled=False)
        result = apply_blur(img, cfg)
        assert result is img

    def test_returns_new_image_when_enabled(self):
        img = _solid()
        cfg = BlurConfig(enabled=True, radius=2.0)
        result = apply_blur(img, cfg)
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self):
        img = _solid(size=(64, 64))
        cfg = BlurConfig(enabled=True, radius=1.0)
        result = apply_blur(img, cfg)
        assert result.size == (64, 64)

    def test_mode_preserved(self):
        img = _solid()
        cfg = BlurConfig(enabled=True)
        result = apply_blur(img, cfg)
        assert result.mode == img.mode


class TestBlurStage:
    def test_returns_same_image_when_config_none(self):
        img = _solid()
        stage = BlurStage(config=None)
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        img = _solid()
        stage = BlurStage(config=BlurConfig(enabled=False))
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        img = _solid()
        stage = BlurStage(config=BlurConfig(enabled=True, radius=1.5))
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_build_blur_stage_returns_stage(self):
        stage = build_blur_stage(BlurConfig(enabled=False))
        assert isinstance(stage, BlurStage)
