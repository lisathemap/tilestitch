"""Tests for tilestitch.pixelshift_pipeline."""
from __future__ import annotations

from PIL import Image

from tilestitch.tile_pixelshift import PixelShiftConfig
from tilestitch.pixelshift_pipeline import PixelShiftStage, build_pixelshift_stage


def _blank(size: int = 64) -> Image.Image:
    return Image.new("RGB", (size, size), (128, 128, 128))


class TestPixelShiftStage:
    def test_returns_same_image_when_config_none(self) -> None:
        stage = PixelShiftStage(None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self) -> None:
        cfg = PixelShiftConfig(x_shift=4, y_shift=0, enabled=False)
        stage = PixelShiftStage(cfg)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self) -> None:
        cfg = PixelShiftConfig(x_shift=4, y_shift=0, enabled=True)
        stage = PixelShiftStage(cfg)
        img = _blank()
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self) -> None:
        cfg = PixelShiftConfig(x_shift=4, y_shift=0)
        stage = PixelShiftStage(cfg)
        img = _blank(64)
        result = stage.process(img)
        assert result.size == (64, 64)

    def test_build_returns_stage(self) -> None:
        cfg = PixelShiftConfig(x_shift=2, y_shift=0)
        stage = build_pixelshift_stage(cfg)
        assert isinstance(stage, PixelShiftStage)

    def test_build_without_config_returns_stage(self, monkeypatch) -> None:
        monkeypatch.setenv("TILESTITCH_PIXELSHIFT_X", "4")
        monkeypatch.setenv("TILESTITCH_PIXELSHIFT_Y", "0")
        monkeypatch.delenv("TILESTITCH_PIXELSHIFT_ENABLED", raising=False)
        stage = build_pixelshift_stage()
        assert isinstance(stage, PixelShiftStage)
