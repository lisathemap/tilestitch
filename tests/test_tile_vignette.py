"""Tests for tilestitch.tile_vignette and vignette_pipeline."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_vignette import (
    VignetteConfig,
    VignetteError,
    apply_vignette,
)
from tilestitch.vignette_pipeline import VignetteStage, build_vignette_stage


def _blank(w: int = 64, h: int = 64) -> Image.Image:
    return Image.new("RGB", (w, h), (200, 200, 200))


class TestVignetteConfig:
    def test_defaults(self):
        cfg = VignetteConfig()
        assert cfg.enabled is True
        assert cfg.strength == 0.5
        assert cfg.radius == 1.0

    def test_zero_strength_raises(self):
        with pytest.raises(VignetteError):
            VignetteConfig(strength=0.0)

    def test_negative_strength_raises(self):
        with pytest.raises(VignetteError):
            VignetteConfig(strength=-0.1)

    def test_strength_above_one_raises(self):
        with pytest.raises(VignetteError):
            VignetteConfig(strength=1.1)

    def test_strength_one_valid(self):
        cfg = VignetteConfig(strength=1.0)
        assert cfg.strength == 1.0

    def test_zero_radius_raises(self):
        with pytest.raises(VignetteError):
            VignetteConfig(radius=0.0)

    def test_negative_radius_raises(self):
        with pytest.raises(VignetteError):
            VignetteConfig(radius=-1.0)

    def test_custom_values_stored(self):
        cfg = VignetteConfig(strength=0.8, radius=0.7)
        assert cfg.strength == 0.8
        assert cfg.radius == 0.7


class TestApplyVignette:
    def test_returns_image(self):
        result = apply_vignette(_blank(), VignetteConfig())
        assert isinstance(result, Image.Image)

    def test_output_is_rgba(self):
        result = apply_vignette(_blank(), VignetteConfig())
        assert result.mode == "RGBA"

    def test_output_size_unchanged(self):
        img = _blank(80, 60)
        result = apply_vignette(img, VignetteConfig())
        assert result.size == (80, 60)

    def test_corners_darker_than_centre(self):
        img = Image.new("RGB", (64, 64), (255, 255, 255))
        result = apply_vignette(img, VignetteConfig(strength=1.0)).convert("RGB")
        centre = result.getpixel((32, 32))
        corner = result.getpixel((0, 0))
        assert sum(corner) < sum(centre)


class TestVignetteStage:
    def test_returns_same_image_when_config_none(self):
        stage = VignetteStage(config=None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        cfg = VignetteConfig(enabled=False)
        stage = VignetteStage(config=cfg)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        cfg = VignetteConfig(enabled=True)
        stage = VignetteStage(config=cfg)
        result = stage.process(_blank())
        assert isinstance(result, Image.Image)

    def test_build_vignette_stage_returns_stage(self):
        stage = build_vignette_stage(VignetteConfig())
        assert isinstance(stage, VignetteStage)
