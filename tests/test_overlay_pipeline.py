"""Tests for tilestitch.overlay_pipeline."""
from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from tilestitch.tile_overlay import OverlayConfig
from tilestitch.overlay_pipeline import OverlayStage, build_overlay_stage


def _blank() -> Image.Image:
    return Image.new("RGB", (64, 64), (100, 100, 100))


def _write_png(path: Path) -> Path:
    img = Image.new("RGBA", (64, 64), (255, 0, 0, 80))
    img.save(path)
    return path


class TestOverlayStage:
    def test_returns_same_image_when_config_none(self) -> None:
        stage = OverlayStage(config=None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self, tmp_path: Path) -> None:
        overlay_file = _write_png(tmp_path / "ov.png")
        cfg = OverlayConfig(path=overlay_file, enabled=False)
        stage = OverlayStage(config=cfg)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self, tmp_path: Path) -> None:
        overlay_file = _write_png(tmp_path / "ov.png")
        cfg = OverlayConfig(path=overlay_file, opacity=0.5)
        stage = OverlayStage(config=cfg)
        result = stage.process(_blank())
        assert isinstance(result, Image.Image)

    def test_build_overlay_stage_none_config(self) -> None:
        stage = build_overlay_stage(config=None)
        assert isinstance(stage, OverlayStage)
        assert stage.config is None

    def test_build_overlay_stage_with_config(self, tmp_path: Path) -> None:
        overlay_file = _write_png(tmp_path / "ov.png")
        cfg = OverlayConfig(path=overlay_file)
        stage = build_overlay_stage(config=cfg)
        assert stage.config is cfg
