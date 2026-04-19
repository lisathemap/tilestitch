import pytest
from PIL import Image

from tilestitch.tile_emboss import (
    EmbossConfig,
    EmbossError,
    apply_emboss,
    emboss_config_from_env,
)
from tilestitch.emboss_pipeline import EmbossStage, build_emboss_stage


def _solid(colour=(128, 128, 128, 255), size=(64, 64)) -> Image.Image:
    img = Image.new("RGBA", size, colour)
    return img


class TestEmbossConfig:
    def test_defaults(self):
        cfg = EmbossConfig()
        assert cfg.enabled is True
        assert cfg.blend == 1.0

    def test_blend_stored(self):
        cfg = EmbossConfig(blend=0.5)
        assert cfg.blend == 0.5

    def test_blend_zero_valid(self):
        cfg = EmbossConfig(blend=0.0)
        assert cfg.blend == 0.0

    def test_blend_one_valid(self):
        cfg = EmbossConfig(blend=1.0)
        assert cfg.blend == 1.0

    def test_blend_above_one_raises(self):
        with pytest.raises(EmbossError):
            EmbossConfig(blend=1.1)

    def test_blend_below_zero_raises(self):
        with pytest.raises(EmbossError):
            EmbossConfig(blend=-0.1)

    def test_invalid_enabled_raises(self):
        with pytest.raises(EmbossError):
            EmbossConfig(enabled="yes")  # type: ignore


class TestApplyEmboss:
    def test_returns_image(self):
        img = _solid()
        result = apply_emboss(img, EmbossConfig())
        assert isinstance(result, Image.Image)

    def test_returns_same_when_disabled(self):
        img = _solid()
        result = apply_emboss(img, EmbossConfig(enabled=False))
        assert result is img

    def test_output_size_unchanged(self):
        img = _solid(size=(32, 32))
        result = apply_emboss(img, EmbossConfig())
        assert result.size == (32, 32)

    def test_zero_blend_returns_original_pixels(self):
        img = _solid(colour=(200, 100, 50, 255))
        result = apply_emboss(img, EmbossConfig(blend=0.0))
        assert result.getpixel((0, 0)) == (200, 100, 50, 255)

    def test_full_blend_differs_from_original(self):
        img = _solid(colour=(200, 100, 50, 255))
        result = apply_emboss(img, EmbossConfig(blend=1.0))
        # Emboss filter changes pixel values
        assert result.getpixel((0, 0)) != (200, 100, 50, 255)


class TestEmbossStage:
    def test_returns_same_image_when_config_none(self):
        stage = EmbossStage(config=None)
        img = _solid()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        stage = EmbossStage(config=EmbossConfig(enabled=False))
        img = _solid()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        stage = EmbossStage(config=EmbossConfig(enabled=True))
        img = _solid()
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_build_emboss_stage_returns_stage(self):
        stage = build_emboss_stage(EmbossConfig())
        assert isinstance(stage, EmbossStage)

    def test_build_emboss_stage_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_EMBOSS_ENABLED", "false")
        stage = build_emboss_stage()
        assert stage.config is not None
        assert stage.config.enabled is False
