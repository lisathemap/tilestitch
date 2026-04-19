"""Tests for tilestitch.tile_overlay."""
from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image

from tilestitch.tile_overlay import OverlayConfig, OverlayError, apply_overlay


def _write_png(path: Path, colour: tuple[int, int, int, int] = (255, 0, 0, 128)) -> Path:
    img = Image.new("RGBA", (64, 64), colour)
    img.save(path)
    return path


@pytest.fixture()
def overlay_file(tmp_path: Path) -> Path:
    return _write_png(tmp_path / "overlay.png")


def _blank(mode: str = "RGB", size: tuple[int, int] = (64, 64)) -> Image.Image:
    return Image.new(mode, size, (200, 200, 200))


class TestOverlayConfig:
    def test_valid_config_stores_path(self, overlay_file: Path) -> None:
        cfg = OverlayConfig(path=overlay_file)
        assert cfg.path == overlay_file

    def test_default_opacity_is_one(self, overlay_file: Path) -> None:
        cfg = OverlayConfig(path=overlay_file)
        assert cfg.opacity == 1.0

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(OverlayError, match="not found"):
            OverlayConfig(path=tmp_path / "missing.png")

    def test_opacity_above_one_raises(self, overlay_file: Path) -> None:
        with pytest.raises(OverlayError, match="opacity"):
            OverlayConfig(path=overlay_file, opacity=1.5)

    def test_opacity_below_zero_raises(self, overlay_file: Path) -> None:
        with pytest.raises(OverlayError, match="opacity"):
            OverlayConfig(path=overlay_file, opacity=-0.1)

    def test_opacity_zero_valid(self, overlay_file: Path) -> None:
        cfg = OverlayConfig(path=overlay_file, opacity=0.0)
        assert cfg.opacity == 0.0


class TestApplyOverlay:
    def test_returns_image(self, overlay_file: Path) -> None:
        cfg = OverlayConfig(path=overlay_file, opacity=0.5)
        result = apply_overlay(_blank(), cfg)
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self, overlay_file: Path) -> None:
        base = _blank(size=(128, 128))
        cfg = OverlayConfig(path=overlay_file)
        result = apply_overlay(base, cfg)
        assert result.size == (128, 128)

    def test_disabled_returns_original(self, overlay_file: Path) -> None:
        base = _blank()
        cfg = OverlayConfig(path=overlay_file, enabled=False)
        result = apply_overlay(base, cfg)
        assert result is base

    def test_rgba_base_preserved(self, overlay_file: Path) -> None:
        base = _blank(mode="RGBA")
        cfg = OverlayConfig(path=overlay_file, opacity=0.5)
        result = apply_overlay(base, cfg)
        assert result.mode == "RGBA"

    def test_rgb_base_returns_rgb(self, overlay_file: Path) -> None:
        base = _blank(mode="RGB")
        cfg = OverlayConfig(path=overlay_file, opacity=0.5)
        result = apply_overlay(base, cfg)
        assert result.mode == "RGB"
