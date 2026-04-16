"""Tests for tilestitch.tile_scaler."""

import pytest
from PIL import Image

from tilestitch.tile_scaler import (
    ScaleMethod,
    ScaleMethodError,
    scale_image,
    scale_tile,
)


def _solid(width: int = 256, height: int = 256, colour: tuple = (128, 64, 32)) -> Image.Image:
    img = Image.new("RGB", (width, height), colour)
    return img


# ---------------------------------------------------------------------------
# ScaleMethod.from_string
# ---------------------------------------------------------------------------

class TestScaleMethodFromString:
    def test_png_lowercase(self):
        assert ScaleMethod.from_string("nearest") is ScaleMethod.NEAREST

    def test_case_insensitive(self):
        assert ScaleMethod.from_string("LANCZOS") is ScaleMethod.LANCZOS

    def test_whitespace_stripped(self):
        assert ScaleMethod.from_string("  bicubic  ") is ScaleMethod.BICUBIC

    def test_unknown_raises(self):
        with pytest.raises(ScaleMethodError):
            ScaleMethod.from_string("magic")

    def test_error_message_contains_input(self):
        with pytest.raises(ScaleMethodError, match="nope"):
            ScaleMethod.from_string("nope")


# ---------------------------------------------------------------------------
# scale_tile
# ---------------------------------------------------------------------------

class TestScaleTile:
    def test_returns_image(self):
        result = scale_tile(_solid(), 128)
        assert isinstance(result, Image.Image)

    def test_output_size_correct(self):
        result = scale_tile(_solid(256, 256), 128)
        assert result.size == (128, 128)

    def test_upscale(self):
        result = scale_tile(_solid(256, 256), 512)
        assert result.size == (512, 512)

    def test_same_size_returns_copy(self):
        src = _solid(256, 256)
        result = scale_tile(src, 256)
        assert result is not src
        assert result.size == (256, 256)

    def test_zero_size_raises(self):
        with pytest.raises(ValueError):
            scale_tile(_solid(), 0)

    def test_negative_size_raises(self):
        with pytest.raises(ValueError):
            scale_tile(_solid(), -1)

    def test_custom_method_accepted(self):
        result = scale_tile(_solid(), 128, method=ScaleMethod.NEAREST)
        assert result.size == (128, 128)


# ---------------------------------------------------------------------------
# scale_image
# ---------------------------------------------------------------------------

class TestScaleImage:
    def test_returns_image(self):
        result = scale_image(_solid(512, 256), 2.0)
        assert isinstance(result, Image.Image)

    def test_doubles_dimensions(self):
        result = scale_image(_solid(100, 50), 2.0)
        assert result.size == (200, 100)

    def test_halves_dimensions(self):
        result = scale_image(_solid(200, 100), 0.5)
        assert result.size == (100, 50)

    def test_factor_one_preserves_size(self):
        src = _solid(300, 300)
        result = scale_image(src, 1.0)
        assert result.size == (300, 300)

    def test_zero_factor_raises(self):
        with pytest.raises(ValueError):
            scale_image(_solid(), 0.0)

    def test_negative_factor_raises(self):
        with pytest.raises(ValueError):
            scale_image(_solid(), -0.5)
