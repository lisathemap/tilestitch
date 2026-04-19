"""Tests for tilestitch.tile_sketch."""
import pytest
from PIL import Image

from tilestitch.tile_sketch import SketchConfig, SketchError, apply_sketch


def _solid(colour=(120, 80, 60), size=(64, 64), mode="RGB") -> Image.Image:
    img = Image.new(mode, size, colour)
    return img


class TestSketchConfig:
    def test_defaults(self):
        cfg = SketchConfig()
        assert cfg.enabled is True
        assert cfg.blend == 0.8

    def test_blend_stored(self):
        cfg = SketchConfig(blend=0.5)
        assert cfg.blend == 0.5

    def test_blend_zero_valid(self):
        cfg = SketchConfig(blend=0.0)
        assert cfg.blend == 0.0

    def test_blend_one_valid(self):
        cfg = SketchConfig(blend=1.0)
        assert cfg.blend == 1.0

    def test_blend_above_one_raises(self):
        with pytest.raises(SketchError):
            SketchConfig(blend=1.1)

    def test_blend_below_zero_raises(self):
        with pytest.raises(SketchError):
            SketchConfig(blend=-0.1)

    def test_invalid_enabled_raises(self):
        with pytest.raises(SketchError):
            SketchConfig(enabled="yes")  # type: ignore


class TestApplySketch:
    def test_returns_image(self):
        img = _solid()
        result = apply_sketch(img, SketchConfig())
        assert isinstance(result, Image.Image)

    def test_same_size(self):
        img = _solid(size=(64, 64))
        result = apply_sketch(img, SketchConfig())
        assert result.size == img.size

    def test_disabled_returns_same_object(self):
        img = _solid()
        result = apply_sketch(img, SketchConfig(enabled=False))
        assert result is img

    def test_rgba_preserved(self):
        img = _solid(colour=(100, 100, 100, 200), mode="RGBA")
        result = apply_sketch(img, SketchConfig())
        assert result.mode == "RGBA"

    def test_rgb_output_for_rgb_input(self):
        img = _solid()
        result = apply_sketch(img, SketchConfig())
        assert result.mode == "RGB"
