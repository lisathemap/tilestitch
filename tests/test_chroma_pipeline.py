"""Tests for tilestitch.chroma_pipeline."""
from __future__ import annotations

from PIL import Image

from tilestitch.tile_chroma import ChromaConfig
from tilestitch.chroma_pipeline import ChromaStage, build_chroma_stage


def _blank(size: tuple = (4, 4)) -> Image.Image:
    return Image.new("RGB", size, (0, 255, 0))


class TestChromaStage:
    def test_returns_same_image_when_config_none(self):
        stage = build_chroma_stage(None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        cfg = ChromaConfig(enabled=False)
        stage = build_chroma_stage(cfg)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        cfg = ChromaConfig(key_colour="#00ff00", replacement_colour="#ff0000", threshold=0)
        stage = build_chroma_stage(cfg)
        img = _blank()
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_replaces_key_colour(self):
        cfg = ChromaConfig(key_colour="#00ff00", replacement_colour="#0000ff", threshold=0)
        stage = build_chroma_stage(cfg)
        img = _blank()
        result = stage.process(img)
        px = result.getpixel((0, 0))
        assert px[:3] == (0, 0, 255)

    def test_build_chroma_stage_returns_stage(self):
        cfg = ChromaConfig()
        stage = build_chroma_stage(cfg)
        assert isinstance(stage, ChromaStage)
