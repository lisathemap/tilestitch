"""Tests for tilestitch.fog_pipeline."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.fog_pipeline import FogStage, build_fog_stage
from tilestitch.tile_fog import FogConfig


def _blank(size: int = 32) -> Image.Image:
    return Image.new("RGB", (size, size), (128, 128, 128))


class TestFogStage:
    def test_returns_same_image_when_config_none(self) -> None:
        stage = FogStage(config=None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self) -> None:
        stage = FogStage(config=FogConfig(enabled=False))
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self) -> None:
        stage = FogStage(config=FogConfig(enabled=True, density=0.5))
        img = _blank()
        result = stage.process(img)
        assert isinstance(result, Image.Image)
        assert result.size == img.size

    def test_build_fog_stage_returns_stage(self) -> None:
        stage = build_fog_stage(config=FogConfig())
        assert isinstance(stage, FogStage)

    def test_build_fog_stage_with_none_uses_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_FOG_ENABLED", "false")
        stage = build_fog_stage(config=None)
        assert stage.config is not None
        assert stage.config.enabled is False
