"""Tests for tilestitch.glitch_pipeline."""

from __future__ import annotations

from PIL import Image

from tilestitch.glitch_pipeline import GlitchStage, build_glitch_stage
from tilestitch.tile_glitch import GlitchConfig


def _blank(size: int = 32) -> Image.Image:
    return Image.new("RGBA", (size, size), (255, 255, 255, 255))


class TestGlitchStage:
    def test_returns_same_image_when_config_none(self) -> None:
        stage = build_glitch_stage(config=None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self) -> None:
        stage = build_glitch_stage(config=GlitchConfig(enabled=False))
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self) -> None:
        stage = build_glitch_stage(config=GlitchConfig(enabled=True, seed=0))
        img = _blank(size=64)
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_output_size_preserved(self) -> None:
        stage = build_glitch_stage(config=GlitchConfig(enabled=True, seed=1))
        img = _blank(size=48)
        result = stage.process(img)
        assert result.size == (48, 48)

    def test_build_stage_stores_config(self) -> None:
        cfg = GlitchConfig(seed=5)
        stage = build_glitch_stage(config=cfg)
        assert stage.config is cfg
