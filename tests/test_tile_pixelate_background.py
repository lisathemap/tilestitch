"""Tests for tile_pixelate_background and pixelate_background_pipeline."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_pixelate_background import (
    PixelateBackgroundConfig,
    PixelateBackgroundError,
    apply_pixelate_background,
    pixelate_background_config_from_env,
)
from tilestitch.pixelate_background_pipeline import (
    PixelateBackgroundStage,
    build_pixelate_background_stage,
)


def _solid(colour: tuple = (100, 150, 200), size: tuple = (64, 64)) -> Image.Image:
    return Image.new("RGB", size, colour)


class TestPixelateBackgroundConfig:
    def test_defaults(self):
        cfg = PixelateBackgroundConfig()
        assert cfg.enabled is True
        assert cfg.block_size == 16
        assert cfg.mask_cx == 0.5
        assert cfg.mask_cy == 0.5
        assert cfg.mask_radius == 0.3

    def test_zero_block_size_raises(self):
        with pytest.raises(PixelateBackgroundError):
            PixelateBackgroundConfig(block_size=0)

    def test_negative_block_size_raises(self):
        with pytest.raises(PixelateBackgroundError):
            PixelateBackgroundConfig(block_size=-1)

    def test_mask_cx_below_zero_raises(self):
        with pytest.raises(PixelateBackgroundError):
            PixelateBackgroundConfig(mask_cx=-0.1)

    def test_mask_cx_above_one_raises(self):
        with pytest.raises(PixelateBackgroundError):
            PixelateBackgroundConfig(mask_cx=1.1)

    def test_mask_cy_below_zero_raises(self):
        with pytest.raises(PixelateBackgroundError):
            PixelateBackgroundConfig(mask_cy=-0.1)

    def test_mask_cy_above_one_raises(self):
        with pytest.raises(PixelateBackgroundError):
            PixelateBackgroundConfig(mask_cy=1.1)

    def test_zero_mask_radius_raises(self):
        with pytest.raises(PixelateBackgroundError):
            PixelateBackgroundConfig(mask_radius=0.0)

    def test_mask_radius_above_one_raises(self):
        with pytest.raises(PixelateBackgroundError):
            PixelateBackgroundConfig(mask_radius=1.1)

    def test_valid_custom_values(self):
        cfg = PixelateBackgroundConfig(block_size=8, mask_cx=0.3, mask_cy=0.7, mask_radius=0.5)
        assert cfg.block_size == 8


class TestApplyPixelateBackground:
    def test_returns_image(self):
        img = _solid()
        cfg = PixelateBackgroundConfig()
        result = apply_pixelate_background(img, cfg)
        assert isinstance(result, Image.Image)

    def test_same_size(self):
        img = _solid(size=(64, 64))
        cfg = PixelateBackgroundConfig()
        result = apply_pixelate_background(img, cfg)
        assert result.size == img.size

    def test_disabled_returns_original(self):
        img = _solid()
        cfg = PixelateBackgroundConfig(enabled=False)
        result = apply_pixelate_background(img, cfg)
        assert result is img

    def test_full_radius_preserves_image_mostly(self):
        img = _solid((200, 100, 50))
        cfg = PixelateBackgroundConfig(mask_radius=1.0)
        result = apply_pixelate_background(img, cfg)
        assert result.size == img.size


class TestPixelateBackgroundStage:
    def test_returns_same_image_when_config_none(self):
        img = _solid()
        stage = PixelateBackgroundStage(config=None)
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        img = _solid()
        cfg = PixelateBackgroundConfig(enabled=False)
        stage = PixelateBackgroundStage(config=cfg)
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        img = _solid()
        cfg = PixelateBackgroundConfig(enabled=True, block_size=4)
        stage = PixelateBackgroundStage(config=cfg)
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_build_stage_returns_stage(self):
        stage = build_pixelate_background_stage(PixelateBackgroundConfig())
        assert isinstance(stage, PixelateBackgroundStage)
