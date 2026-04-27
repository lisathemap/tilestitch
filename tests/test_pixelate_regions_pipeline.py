"""Tests for tilestitch.pixelate_regions_pipeline."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_pixelate_regions import PixelateRegionsConfig
from tilestitch.pixelate_regions_pipeline import (
    PixelateRegionsStage,
    build_pixelate_regions_stage,
)


def _blank(size: int = 64) -> Image.Image:
    return Image.new("RGBA", (size, size), (0, 0, 0, 255))


class TestPixelateRegionsStage:
    def test_returns_same_image_when_config_none(self):
        stage = PixelateRegionsStage(config=None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        cfg = PixelateRegionsConfig(
            regions=[(0, 0, 32, 32)], enabled=False
        )
        stage = PixelateRegionsStage(config=cfg)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_no_regions(self):
        cfg = PixelateRegionsConfig(regions=[])
        stage = PixelateRegionsStage(config=cfg)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        cfg = PixelateRegionsConfig(
            regions=[(0, 0, 32, 32)], block_size=8, enabled=True
        )
        stage = PixelateRegionsStage(config=cfg)
        img = _blank()
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self):
        cfg = PixelateRegionsConfig(
            regions=[(0, 0, 64, 64)], block_size=16
        )
        stage = PixelateRegionsStage(config=cfg)
        img = _blank(size=64)
        result = stage.process(img)
        assert result.size == (64, 64)


class TestBuildPixelateRegionsStage:
    def test_returns_stage_instance(self):
        stage = build_pixelate_regions_stage()
        assert isinstance(stage, PixelateRegionsStage)

    def test_accepts_explicit_config(self):
        cfg = PixelateRegionsConfig(regions=[(0, 0, 10, 10)])
        stage = build_pixelate_regions_stage(config=cfg)
        assert stage.config is cfg

    def test_none_config_builds_default(self):
        stage = build_pixelate_regions_stage(config=None)
        assert stage.config is not None
        assert isinstance(stage.config, PixelateRegionsConfig)
