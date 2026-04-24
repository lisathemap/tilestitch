"""Tests for tilestitch.spotlight_pipeline."""

import pytest
from PIL import Image

from tilestitch.tile_spotlight import SpotlightConfig
from tilestitch.spotlight_pipeline import SpotlightStage, build_spotlight_stage


def _blank(size: int = 32) -> Image.Image:
    return Image.new("RGB", (size, size), (100, 100, 100))


class TestSpotlightStage:
    def test_returns_same_image_when_config_none(self):
        stage = SpotlightStage(config=None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        cfg = SpotlightConfig(enabled=False)
        stage = SpotlightStage(config=cfg)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        cfg = SpotlightConfig(enabled=True)
        stage = SpotlightStage(config=cfg)
        img = _blank()
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_output_size_preserved(self):
        cfg = SpotlightConfig()
        stage = SpotlightStage(config=cfg)
        img = _blank(size=48)
        result = stage.process(img)
        assert result.size == (48, 48)

    def test_build_spotlight_stage_returns_stage(self):
        cfg = SpotlightConfig()
        stage = build_spotlight_stage(cfg)
        assert isinstance(stage, SpotlightStage)

    def test_build_spotlight_stage_uses_env_when_no_config(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_SPOTLIGHT_ENABLED", raising=False)
        stage = build_spotlight_stage()
        assert isinstance(stage, SpotlightStage)
        assert stage.config is not None
