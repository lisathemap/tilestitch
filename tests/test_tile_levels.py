"""Tests for tilestitch.tile_levels."""

from __future__ import annotations

import os

import pytest
from PIL import Image

from tilestitch.tile_levels import (
    LevelsConfig,
    LevelsError,
    apply_levels,
    levels_config_from_env,
)


def _solid(colour: tuple[int, ...], size: tuple[int, int] = (4, 4)) -> Image.Image:
    mode = "RGBA" if len(colour) == 4 else "RGB"
    img = Image.new(mode, size, colour)
    return img


# ---------------------------------------------------------------------------
# LevelsConfig defaults
# ---------------------------------------------------------------------------

class TestLevelsConfig:
    def test_defaults(self) -> None:
        cfg = LevelsConfig()
        assert cfg.in_low == 0
        assert cfg.in_high == 255
        assert cfg.gamma == 1.0
        assert cfg.out_low == 0
        assert cfg.out_high == 255
        assert cfg.enabled is True

    def test_in_low_too_high_raises(self) -> None:
        with pytest.raises(LevelsError):
            LevelsConfig(in_low=255, in_high=255)

    def test_in_high_must_exceed_in_low(self) -> None:
        with pytest.raises(LevelsError):
            LevelsConfig(in_low=100, in_high=100)

    def test_in_high_below_range_raises(self) -> None:
        with pytest.raises(LevelsError):
            LevelsConfig(in_high=0)

    def test_gamma_zero_raises(self) -> None:
        with pytest.raises(LevelsError):
            LevelsConfig(gamma=0.0)

    def test_negative_gamma_raises(self) -> None:
        with pytest.raises(LevelsError):
            LevelsConfig(gamma=-1.0)

    def test_out_high_must_exceed_out_low(self) -> None:
        with pytest.raises(LevelsError):
            LevelsConfig(out_low=200, out_high=200)

    def test_out_low_above_254_raises(self) -> None:
        with pytest.raises(LevelsError):
            LevelsConfig(out_low=255)

    def test_valid_custom_values(self) -> None:
        cfg = LevelsConfig(in_low=10, in_high=240, gamma=1.5, out_low=5, out_high=250)
        assert cfg.in_low == 10
        assert cfg.gamma == 1.5


# ---------------------------------------------------------------------------
# apply_levels
# ---------------------------------------------------------------------------

class TestApplyLevels:
    def test_returns_image(self) -> None:
        img = _solid((128, 128, 128))
        cfg = LevelsConfig()
        result = apply_levels(img, cfg)
        assert isinstance(result, Image.Image)

    def test_disabled_returns_original(self) -> None:
        img = _solid((100, 150, 200))
        cfg = LevelsConfig(enabled=False)
        result = apply_levels(img, cfg)
        assert result is img

    def test_rgba_image_alpha_preserved(self) -> None:
        img = _solid((100, 100, 100, 128))
        cfg = LevelsConfig()
        result = apply_levels(img, cfg)
        assert result.mode == "RGBA"
        # Alpha channel should be unchanged
        assert result.getpixel((0, 0))[3] == 128

    def test_output_size_unchanged(self) -> None:
        img = _solid((80, 80, 80), size=(16, 8))
        cfg = LevelsConfig(in_low=0, in_high=200)
        result = apply_levels(img, cfg)
        assert result.size == (16, 8)


# ---------------------------------------------------------------------------
# levels_config_from_env
# ---------------------------------------------------------------------------

class TestLevelsConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for key in (
            "TILESTITCH_LEVELS_IN_LOW", "TILESTITCH_LEVELS_IN_HIGH",
            "TILESTITCH_LEVELS_GAMMA", "TILESTITCH_LEVELS_OUT_LOW",
            "TILESTITCH_LEVELS_OUT_HIGH", "TILESTITCH_LEVELS_ENABLED",
        ):
            monkeypatch.delenv(key, raising=False)
        cfg = levels_config_from_env()
        assert cfg.in_low == 0
        assert cfg.in_high == 255
        assert cfg.gamma == 1.0
        assert cfg.enabled is True

    def test_reads_env_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_LEVELS_IN_LOW", "20")
        monkeypatch.setenv("TILESTITCH_LEVELS_IN_HIGH", "230")
        monkeypatch.setenv("TILESTITCH_LEVELS_GAMMA", "0.8")
        monkeypatch.setenv("TILESTITCH_LEVELS_OUT_LOW", "10")
        monkeypatch.setenv("TILESTITCH_LEVELS_OUT_HIGH", "245")
        cfg = levels_config_from_env()
        assert cfg.in_low == 20
        assert cfg.in_high == 230
        assert cfg.gamma == pytest.approx(0.8)
        assert cfg.out_low == 10
        assert cfg.out_high == 245

    def test_disabled_via_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_LEVELS_ENABLED", "false")
        cfg = levels_config_from_env()
        assert cfg.enabled is False
