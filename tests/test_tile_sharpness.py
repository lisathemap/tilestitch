"""Tests for tilestitch.tile_sharpness."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_sharpness import (
    SharpnessResult,
    SharpnessScoreError,
    score_sharpness,
)


def _solid(colour: tuple, size: tuple = (64, 64)) -> Image.Image:
    img = Image.new("RGB", size, colour)
    return img


def _noisy(size: tuple = (64, 64)) -> Image.Image:
    import random
    img = Image.new("RGB", size)
    pixels = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
              for _ in range(size[0] * size[1])]
    img.putdata(pixels)
    return img


# ---------------------------------------------------------------------------
# SharpnessResult
# ---------------------------------------------------------------------------

class TestSharpnessResult:
    def test_valid_result_stores_fields(self):
        r = SharpnessResult(score=200.0, is_blurry=False, threshold=100.0)
        assert r.score == 200.0
        assert r.is_blurry is False
        assert r.threshold == 100.0

    def test_negative_score_raises(self):
        with pytest.raises(SharpnessScoreError):
            SharpnessResult(score=-1.0, is_blurry=False, threshold=100.0)

    def test_zero_threshold_raises(self):
        with pytest.raises(SharpnessScoreError):
            SharpnessResult(score=10.0, is_blurry=False, threshold=0.0)

    def test_negative_threshold_raises(self):
        with pytest.raises(SharpnessScoreError):
            SharpnessResult(score=10.0, is_blurry=False, threshold=-5.0)


# ---------------------------------------------------------------------------
# score_sharpness
# ---------------------------------------------------------------------------

class TestScoreSharpness:
    def test_returns_sharpness_result(self):
        img = _solid((128, 128, 128))
        result = score_sharpness(img)
        assert isinstance(result, SharpnessResult)

    def test_solid_image_is_blurry(self):
        img = _solid((200, 100, 50))
        result = score_sharpness(img, threshold=100.0)
        assert result.is_blurry is True

    def test_noisy_image_is_not_blurry(self):
        img = _noisy()
        result = score_sharpness(img, threshold=10.0)
        assert result.is_blurry is False

    def test_score_is_non_negative(self):
        img = _solid((0, 0, 0))
        result = score_sharpness(img)
        assert result.score >= 0.0

    def test_threshold_stored_in_result(self):
        img = _solid((10, 10, 10))
        result = score_sharpness(img, threshold=42.5)
        assert result.threshold == 42.5

    def test_non_image_raises(self):
        with pytest.raises(SharpnessScoreError):
            score_sharpness("not an image")  # type: ignore

    def test_zero_threshold_raises(self):
        img = _solid((0, 0, 0))
        with pytest.raises(SharpnessScoreError):
            score_sharpness(img, threshold=0.0)

    def test_negative_threshold_raises(self):
        img = _solid((0, 0, 0))
        with pytest.raises(SharpnessScoreError):
            score_sharpness(img, threshold=-1.0)

    def test_rgba_image_accepted(self):
        img = Image.new("RGBA", (32, 32), (255, 0, 0, 128))
        result = score_sharpness(img)
        assert isinstance(result, SharpnessResult)
