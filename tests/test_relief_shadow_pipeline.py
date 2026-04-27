"""Tests for tilestitch.relief_shadow_pipeline."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_relief_shadow import ReliefShadowConfig
from tilestitch.relief_shadow_pipeline import (
    ReliefShadowStage,
    build_relief_shadow_stage,
)


def _blank(size=(64, 64)) -> Image.Image:
    return Image.new("RGBA", size, (128, 128, 128, 255))


class TestReliefShadowStage:
    def test_returns_same_image_when_config_none(self):
        stage = ReliefShadowStage(config=None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        cfg = ReliefShadowConfig(enabled=False)
        stage = ReliefShadowStage(config=cfg)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        cfg = ReliefShadowConfig(enabled=True, blur_radius=0.0, distance=2)
        stage = ReliefShadowStage(config=cfg)
        img = _blank()
        result = stage.process(img)
        assert isinstance(result, Image.Image)
        assert result.size == img.size

    def test_build_with_none_config(self):
        stage = build_relief_shadow_stage(config=None)
        assert stage.config is None

    def test_build_with_explicit_config(self):
        cfg = ReliefShadowConfig(distance=6)
        stage = build_relief_shadow_stage(config=cfg)
        assert stage.config is cfg

    def test_build_from_env_returns_stage(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SHADOW_ENABLED", "true")
        monkeypatch.setenv("TILESTITCH_SHADOW_DISTANCE", "3")
        monkeypatch.setenv("TILESTITCH_SHADOW_OPACITY", "0.4")
        stage = build_relief_shadow_stage(from_env=True)
        assert isinstance(stage, ReliefShadowStage)
        assert stage.config is not None
        assert stage.config.distance == 3
        assert stage.config.opacity == pytest.approx(0.4)

    def test_output_is_rgba(self):
        cfg = ReliefShadowConfig()
        stage = ReliefShadowStage(config=cfg)
        img = Image.new("RGB", (32, 32), (100, 100, 100))
        result = stage.process(img)
        assert result.mode == "RGBA"
