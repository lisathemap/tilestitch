"""Tests for tilestitch.tile_pixelshift."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_pixelshift import (
    PixelShiftConfig,
    PixelShiftError,
    apply_pixelshift,
    pixelshift_config_from_env,
)


def _solid(colour: tuple[int, int, int] = (200, 100, 50), size: int = 64) -> Image.Image:
    return Image.new("RGB", (size, size), colour)


class TestPixelShiftConfig:
    def test_defaults(self) -> None:
        cfg = PixelShiftConfig()
        assert cfg.x_shift == 4
        assert cfg.y_shift == 0
        assert cfg.enabled is True

    def test_x_shift_stored(self) -> None:
        cfg = PixelShiftConfig(x_shift=10, y_shift=0)
        assert cfg.x_shift == 10

    def test_y_shift_stored(self) -> None:
        cfg = PixelShiftConfig(x_shift=0, y_shift=8)
        assert cfg.y_shift == 8

    def test_zero_both_raises(self) -> None:
        with pytest.raises(PixelShiftError, match="non-zero"):
            PixelShiftConfig(x_shift=0, y_shift=0)

    def test_non_integer_x_raises(self) -> None:
        with pytest.raises(PixelShiftError, match="integer"):
            PixelShiftConfig(x_shift=1.5, y_shift=0)  # type: ignore[arg-type]

    def test_non_integer_y_raises(self) -> None:
        with pytest.raises(PixelShiftError, match="integer"):
            PixelShiftConfig(x_shift=2, y_shift="bad")  # type: ignore[arg-type]

    def test_negative_shift_valid(self) -> None:
        cfg = PixelShiftConfig(x_shift=-3, y_shift=0)
        assert cfg.x_shift == -3

    def test_enabled_false_stored(self) -> None:
        cfg = PixelShiftConfig(x_shift=2, y_shift=0, enabled=False)
        assert cfg.enabled is False


class TestApplyPixelShift:
    def test_returns_image(self) -> None:
        img = _solid()
        cfg = PixelShiftConfig(x_shift=4, y_shift=0)
        result = apply_pixelshift(img, cfg)
        assert isinstance(result, Image.Image)

    def test_output_same_size(self) -> None:
        img = _solid(size=64)
        cfg = PixelShiftConfig(x_shift=4, y_shift=0)
        result = apply_pixelshift(img, cfg)
        assert result.size == img.size

    def test_output_mode_preserved_rgb(self) -> None:
        img = _solid()
        cfg = PixelShiftConfig(x_shift=4, y_shift=0)
        result = apply_pixelshift(img, cfg)
        assert result.mode == "RGB"

    def test_output_mode_preserved_rgba(self) -> None:
        img = Image.new("RGBA", (64, 64), (200, 100, 50, 255))
        cfg = PixelShiftConfig(x_shift=4, y_shift=0)
        result = apply_pixelshift(img, cfg)
        assert result.mode == "RGBA"

    def test_channels_differ_from_original(self) -> None:
        img = _solid((180, 90, 40))
        cfg = PixelShiftConfig(x_shift=8, y_shift=0)
        result = apply_pixelshift(img, cfg)
        # After shifting, at least some pixels should differ
        assert list(result.getdata()) != list(img.getdata())


class TestPixelShiftConfigFromEnv:
    def test_defaults_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("TILESTITCH_PIXELSHIFT_X", raising=False)
        monkeypatch.delenv("TILESTITCH_PIXELSHIFT_Y", raising=False)
        monkeypatch.delenv("TILESTITCH_PIXELSHIFT_ENABLED", raising=False)
        cfg = pixelshift_config_from_env()
        assert cfg.x_shift == 4
        assert cfg.y_shift == 0
        assert cfg.enabled is True

    def test_reads_x_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_PIXELSHIFT_X", "12")
        monkeypatch.setenv("TILESTITCH_PIXELSHIFT_Y", "0")
        cfg = pixelshift_config_from_env()
        assert cfg.x_shift == 12

    def test_reads_enabled_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_PIXELSHIFT_ENABLED", "false")
        monkeypatch.setenv("TILESTITCH_PIXELSHIFT_X", "4")
        monkeypatch.setenv("TILESTITCH_PIXELSHIFT_Y", "0")
        cfg = pixelshift_config_from_env()
        assert cfg.enabled is False

    def test_invalid_x_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_PIXELSHIFT_X", "abc")
        with pytest.raises(PixelShiftError, match="integer"):
            pixelshift_config_from_env()
