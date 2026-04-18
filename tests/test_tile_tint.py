"""Tests for tile_tint and tint_pipeline."""
import pytest
from PIL import Image

from tilestitch.tile_tint import (
    TintConfig,
    TintError,
    apply_tint,
    tint_config_from_env,
)
from tilestitch.tint_pipeline import TintStage, build_tint_stage


def _solid(colour=(200, 200, 200), size=(64, 64)) -> Image.Image:
    img = Image.new("RGB", size, colour)
    return img


class TestTintConfig:
    def test_defaults(self):
        cfg = TintConfig()
        assert cfg.colour == "ff0000"
        assert cfg.strength == pytest.approx(0.3)
        assert cfg.enabled is True

    def test_rgb_property(self):
        cfg = TintConfig(colour="00ff80")
        assert cfg.rgb == (0, 255, 128)

    def test_invalid_hex_raises(self):
        with pytest.raises(TintError):
            TintConfig(colour="zzzzzz")

    def test_short_hex_raises(self):
        with pytest.raises(TintError):
            TintConfig(colour="fff")

    def test_zero_strength_raises(self):
        with pytest.raises(TintError):
            TintConfig(strength=0.0)

    def test_negative_strength_raises(self):
        with pytest.raises(TintError):
            TintConfig(strength=-0.1)

    def test_strength_above_one_raises(self):
        with pytest.raises(TintError):
            TintConfig(strength=1.1)

    def test_strength_one_valid(self):
        cfg = TintConfig(strength=1.0)
        assert cfg.strength == 1.0


class TestApplyTint:
    def test_returns_image(self):
        img = _solid()
        cfg = TintConfig(colour="0000ff", strength=0.5)
        result = apply_tint(img, cfg)
        assert isinstance(result, Image.Image)

    def test_output_same_size(self):
        img = _solid(size=(100, 80))
        cfg = TintConfig()
        result = apply_tint(img, cfg)
        assert result.size == (100, 80)

    def test_output_preserves_mode(self):
        img = _solid()
        assert img.mode == "RGB"
        cfg = TintConfig()
        result = apply_tint(img, cfg)
        assert result.mode == "RGB"

    def test_disabled_returns_original(self):
        img = _solid()
        cfg = TintConfig(enabled=False)
        result = apply_tint(img, cfg)
        assert result is img

    def test_blue_tint_shifts_channel(self):
        img = _solid(colour=(100, 100, 100))
        cfg = TintConfig(colour="0000ff", strength=0.5)
        result = apply_tint(img, cfg)
        px = result.getpixel((0, 0))
        assert px[2] > px[0], "blue channel should be boosted"


class TestTintStage:
    def test_returns_same_image_when_config_none(self):
        stage = build_tint_stage(None)
        img = _solid()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        cfg = TintConfig(enabled=False)
        stage = build_tint_stage(cfg)
        img = _solid()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        cfg = TintConfig(colour="ff0000", strength=0.2, enabled=True)
        stage = build_tint_stage(cfg)
        img = _solid()
        result = stage.process(img)
        assert isinstance(result, Image.Image)
