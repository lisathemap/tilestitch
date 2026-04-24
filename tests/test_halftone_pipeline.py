"""Tests for tilestitch.halftone_pipeline."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_halftone import HalftoneConfig
from tilestitch.halftone_pipeline import HalftoneStage, build_halftone_stage


def _blank(size: int = 32) -> Image.Image:
    return Image.new("RGB", (size, size), (200, 200, 200))


class TestHalftoneStage:
    def test_returns_same_image_when_config_none(self):
        img = _blank()
        stage = HalftoneStage(config=None)
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        img = _blank()
        cfg = HalftoneConfig(enabled=False)
        stage = HalftoneStage(config=cfg)
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        img = _blank()
        cfg = HalftoneConfig(enabled=True, dot_size=4)
        stage = HalftoneStage(config=cfg)
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_output_size_preserved(self):
        img = _blank(size=48)
        cfg = HalftoneConfig(dot_size=4)
        stage = HalftoneStage(config=cfg)
        result = stage.process(img)
        assert result.size == (48, 48)


class TestBuildHalftoneStage:
    def test_none_config_returns_disabled_stage(self):
        stage = build_halftone_stage(None)
        assert stage.config is None

    def test_config_stored(self):
        cfg = HalftoneConfig(dot_size=8)
        stage = build_halftone_stage(cfg)
        assert stage.config is cfg

    def test_returns_halftone_stage_instance(self):
        stage = build_halftone_stage()
        assert isinstance(stage, HalftoneStage)
