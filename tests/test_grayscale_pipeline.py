from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_grayscale import GrayscaleConfig
from tilestitch.tile_grayscale_pipeline import GrayscaleStage, build_grayscale_stage


def _blank(mode: str = "RGB") -> Image.Image:
    return Image.new(mode, (64, 64), color=(100, 149, 237))


class TestGrayscaleStage:
    def test_returns_same_image_when_config_none(self):
        stage = build_grayscale_stage(None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        cfg = GrayscaleConfig(enabled=False)
        stage = build_grayscale_stage(cfg)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        cfg = GrayscaleConfig(enabled=True)
        stage = build_grayscale_stage(cfg)
        img = _blank("RGB")
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_output_is_grayscale_mode(self):
        cfg = GrayscaleConfig(enabled=True)
        stage = build_grayscale_stage(cfg)
        result = stage.process(_blank("RGB"))
        assert result.mode in ("L", "LA", "RGB", "RGBA")

    def test_rgba_input_processed(self):
        cfg = GrayscaleConfig(enabled=True)
        stage = build_grayscale_stage(cfg)
        img = _blank("RGBA")
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_build_grayscale_stage_returns_stage(self):
        stage = build_grayscale_stage()
        assert isinstance(stage, GrayscaleStage)

    def test_disabled_config_is_noop(self):
        cfg = GrayscaleConfig(enabled=False)
        stage = GrayscaleStage(cfg)
        img = _blank()
        result = stage.process(img)
        assert result is img
