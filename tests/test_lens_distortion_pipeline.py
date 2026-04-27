"""Tests for tilestitch.lens_distortion_pipeline."""

from __future__ import annotations

from PIL import Image

from tilestitch.lens_distortion_pipeline import (
    LensDistortionStage,
    build_lens_distortion_stage,
)
from tilestitch.tile_lens_distortion import LensDistortionConfig


def _blank(size: tuple = (32, 32)) -> Image.Image:
    return Image.new("RGBA", size, (100, 100, 100, 255))


class TestLensDistortionStage:
    def test_returns_same_image_when_config_none(self):
        stage = LensDistortionStage(config=None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        cfg = LensDistortionConfig(enabled=False)
        stage = LensDistortionStage(config=cfg)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        cfg = LensDistortionConfig(k1=0.2, enabled=True)
        stage = LensDistortionStage(config=cfg)
        img = _blank()
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_output_size_preserved(self):
        cfg = LensDistortionConfig(k1=0.1)
        stage = LensDistortionStage(config=cfg)
        img = _blank(size=(48, 48))
        result = stage.process(img)
        assert result.size == (48, 48)

    def test_build_returns_stage_instance(self):
        cfg = LensDistortionConfig()
        stage = build_lens_distortion_stage(config=cfg)
        assert isinstance(stage, LensDistortionStage)

    def test_build_without_config_uses_defaults(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_LENS_K1", raising=False)
        monkeypatch.delenv("TILESTITCH_LENS_K2", raising=False)
        monkeypatch.delenv("TILESTITCH_LENS_ENABLED", raising=False)
        stage = build_lens_distortion_stage()
        assert stage.config is not None
        assert stage.config.k1 == 0.1
