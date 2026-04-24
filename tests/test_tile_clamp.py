"""Tests for tilestitch.tile_clamp."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_clamp import (
    ClampConfig,
    ClampError,
    apply_clamp,
    clamp_config_from_env,
)


def _solid(r: int, g: int, b: int, size: int = 4) -> Image.Image:
    img = Image.new("RGB", (size, size), (r, g, b))
    return img


# ---------------------------------------------------------------------------
# ClampConfig
# ---------------------------------------------------------------------------

class TestClampConfig:
    def test_defaults(self) -> None:
        cfg = ClampConfig()
        assert cfg.enabled is True
        assert cfg.low == 0
        assert cfg.high == 255

    def test_low_stored(self) -> None:
        cfg = ClampConfig(low=10, high=200)
        assert cfg.low == 10

    def test_high_stored(self) -> None:
        cfg = ClampConfig(low=10, high=200)
        assert cfg.high == 200

    def test_low_equal_high_raises(self) -> None:
        with pytest.raises(ClampError):
            ClampConfig(low=128, high=128)

    def test_low_greater_than_high_raises(self) -> None:
        with pytest.raises(ClampError):
            ClampConfig(low=200, high=100)

    def test_low_negative_raises(self) -> None:
        with pytest.raises(ClampError):
            ClampConfig(low=-1, high=255)

    def test_high_above_255_raises(self) -> None:
        with pytest.raises(ClampError):
            ClampConfig(low=0, high=256)

    def test_low_255_raises_because_equal_or_greater(self) -> None:
        with pytest.raises(ClampError):
            ClampConfig(low=255, high=255)


# ---------------------------------------------------------------------------
# apply_clamp
# ---------------------------------------------------------------------------

class TestApplyClamp:
    def test_returns_image(self) -> None:
        img = _solid(100, 150, 200)
        result = apply_clamp(img, ClampConfig())
        assert isinstance(result, Image.Image)

    def test_output_is_rgba(self) -> None:
        img = _solid(100, 150, 200)
        result = apply_clamp(img, ClampConfig())
        assert result.mode == "RGBA"

    def test_values_within_range_unchanged(self) -> None:
        img = _solid(100, 150, 200)
        result = apply_clamp(img, ClampConfig(low=50, high=210))
        px = result.getpixel((0, 0))
        assert px[0] == 100
        assert px[1] == 150
        assert px[2] == 200

    def test_values_below_low_clamped(self) -> None:
        img = _solid(10, 20, 30)
        result = apply_clamp(img, ClampConfig(low=50, high=200))
        px = result.getpixel((0, 0))
        assert px[0] == 50
        assert px[1] == 50
        assert px[2] == 50

    def test_values_above_high_clamped(self) -> None:
        img = _solid(240, 250, 255)
        result = apply_clamp(img, ClampConfig(low=0, high=200))
        px = result.getpixel((0, 0))
        assert px[0] == 200
        assert px[1] == 200
        assert px[2] == 200

    def test_disabled_returns_original(self) -> None:
        img = _solid(10, 10, 10)
        result = apply_clamp(img, ClampConfig(enabled=False, low=50, high=200))
        assert result is img

    def test_alpha_preserved(self) -> None:
        img = Image.new("RGBA", (4, 4), (100, 100, 100, 128))
        result = apply_clamp(img, ClampConfig(low=0, high=200))
        assert result.getpixel((0, 0))[3] == 128


# ---------------------------------------------------------------------------
# clamp_config_from_env
# ---------------------------------------------------------------------------

class TestClampConfigFromEnv:
    def test_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("TILESTITCH_CLAMP_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_CLAMP_LOW", raising=False)
        monkeypatch.delenv("TILESTITCH_CLAMP_HIGH", raising=False)
        cfg = clamp_config_from_env()
        assert cfg.enabled is True
        assert cfg.low == 0
        assert cfg.high == 255

    def test_disabled_via_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_CLAMP_ENABLED", "0")
        cfg = clamp_config_from_env()
        assert cfg.enabled is False

    def test_custom_range_via_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_CLAMP_LOW", "20")
        monkeypatch.setenv("TILESTITCH_CLAMP_HIGH", "220")
        cfg = clamp_config_from_env()
        assert cfg.low == 20
        assert cfg.high == 220
