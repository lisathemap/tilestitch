"""Tests for tilestitch.tile_relief_shadow."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_relief_shadow import (
    ReliefShadowConfig,
    ReliefShadowError,
    apply_relief_shadow,
)


def _solid(colour=(100, 150, 200, 255), size=(64, 64)) -> Image.Image:
    img = Image.new("RGBA", size, colour)
    return img


# ---------------------------------------------------------------------------
# ReliefShadowConfig
# ---------------------------------------------------------------------------

class TestReliefShadowConfig:
    def test_defaults(self):
        cfg = ReliefShadowConfig()
        assert cfg.enabled is True
        assert cfg.angle == 315.0
        assert cfg.distance == 4
        assert cfg.blur_radius == 2.0
        assert cfg.opacity == 0.5
        assert cfg.colour == (0, 0, 0)

    def test_opacity_zero_valid(self):
        cfg = ReliefShadowConfig(opacity=0.0)
        assert cfg.opacity == 0.0

    def test_opacity_one_valid(self):
        cfg = ReliefShadowConfig(opacity=1.0)
        assert cfg.opacity == 1.0

    def test_opacity_above_one_raises(self):
        with pytest.raises(ReliefShadowError, match="opacity"):
            ReliefShadowConfig(opacity=1.1)

    def test_opacity_below_zero_raises(self):
        with pytest.raises(ReliefShadowError, match="opacity"):
            ReliefShadowConfig(opacity=-0.1)

    def test_negative_distance_raises(self):
        with pytest.raises(ReliefShadowError, match="distance"):
            ReliefShadowConfig(distance=-1)

    def test_zero_distance_valid(self):
        cfg = ReliefShadowConfig(distance=0)
        assert cfg.distance == 0

    def test_negative_blur_raises(self):
        with pytest.raises(ReliefShadowError, match="blur_radius"):
            ReliefShadowConfig(blur_radius=-1.0)

    def test_zero_blur_valid(self):
        cfg = ReliefShadowConfig(blur_radius=0.0)
        assert cfg.blur_radius == 0.0

    def test_custom_colour_stored(self):
        cfg = ReliefShadowConfig(colour=(10, 20, 30))
        assert cfg.colour == (10, 20, 30)


# ---------------------------------------------------------------------------
# apply_relief_shadow
# ---------------------------------------------------------------------------

class TestApplyReliefShadow:
    def test_returns_rgba_image(self):
        img = _solid()
        cfg = ReliefShadowConfig()
        result = apply_relief_shadow(img, cfg)
        assert result.mode == "RGBA"

    def test_output_size_unchanged(self):
        img = _solid(size=(80, 60))
        cfg = ReliefShadowConfig()
        result = apply_relief_shadow(img, cfg)
        assert result.size == (80, 60)

    def test_disabled_returns_original(self):
        img = _solid()
        cfg = ReliefShadowConfig(enabled=False)
        result = apply_relief_shadow(img, cfg)
        assert result is img

    def test_zero_distance_no_crash(self):
        img = _solid()
        cfg = ReliefShadowConfig(distance=0, blur_radius=0.0)
        result = apply_relief_shadow(img, cfg)
        assert result.size == img.size

    def test_fully_transparent_source_no_crash(self):
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        cfg = ReliefShadowConfig()
        result = apply_relief_shadow(img, cfg)
        assert result.size == (32, 32)

    def test_accepts_rgb_image(self):
        img = Image.new("RGB", (32, 32), (200, 100, 50))
        cfg = ReliefShadowConfig()
        result = apply_relief_shadow(img, cfg)
        assert result.mode == "RGBA"
