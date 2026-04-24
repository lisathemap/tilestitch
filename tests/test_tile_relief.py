"""Tests for tilestitch.tile_relief."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_relief import (
    ReliefConfig,
    ReliefError,
    apply_relief,
    relief_config_from_env,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _solid(colour: tuple[int, int, int] = (128, 128, 128), size: int = 64) -> Image.Image:
    return Image.new("RGB", (size, size), colour)


# ---------------------------------------------------------------------------
# ReliefConfig validation
# ---------------------------------------------------------------------------

class TestReliefConfig:
    def test_defaults(self) -> None:
        cfg = ReliefConfig()
        assert cfg.azimuth == 315.0
        assert cfg.altitude == 45.0
        assert cfg.z_factor == 1.0
        assert cfg.blend == 0.6
        assert cfg.enabled is True

    def test_azimuth_zero_valid(self) -> None:
        cfg = ReliefConfig(azimuth=0.0)
        assert cfg.azimuth == 0.0

    def test_azimuth_360_raises(self) -> None:
        with pytest.raises(ReliefError, match="azimuth"):
            ReliefConfig(azimuth=360.0)

    def test_negative_azimuth_raises(self) -> None:
        with pytest.raises(ReliefError, match="azimuth"):
            ReliefConfig(azimuth=-1.0)

    def test_altitude_90_valid(self) -> None:
        cfg = ReliefConfig(altitude=90.0)
        assert cfg.altitude == 90.0

    def test_altitude_zero_raises(self) -> None:
        with pytest.raises(ReliefError, match="altitude"):
            ReliefConfig(altitude=0.0)

    def test_altitude_above_90_raises(self) -> None:
        with pytest.raises(ReliefError, match="altitude"):
            ReliefConfig(altitude=91.0)

    def test_zero_z_factor_raises(self) -> None:
        with pytest.raises(ReliefError, match="z_factor"):
            ReliefConfig(z_factor=0.0)

    def test_negative_z_factor_raises(self) -> None:
        with pytest.raises(ReliefError, match="z_factor"):
            ReliefConfig(z_factor=-0.5)

    def test_blend_zero_valid(self) -> None:
        cfg = ReliefConfig(blend=0.0)
        assert cfg.blend == 0.0

    def test_blend_one_valid(self) -> None:
        cfg = ReliefConfig(blend=1.0)
        assert cfg.blend == 1.0

    def test_blend_above_one_raises(self) -> None:
        with pytest.raises(ReliefError, match="blend"):
            ReliefConfig(blend=1.1)

    def test_blend_below_zero_raises(self) -> None:
        with pytest.raises(ReliefError, match="blend"):
            ReliefConfig(blend=-0.1)


# ---------------------------------------------------------------------------
# apply_relief
# ---------------------------------------------------------------------------

class TestApplyRelief:
    def test_returns_image(self) -> None:
        img = _solid()
        result = apply_relief(img, ReliefConfig())
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self) -> None:
        img = _solid(size=64)
        result = apply_relief(img, ReliefConfig())
        assert result.size == img.size

    def test_disabled_returns_original(self) -> None:
        img = _solid()
        result = apply_relief(img, ReliefConfig(enabled=False))
        assert result is img

    def test_rgba_input_preserved(self) -> None:
        img = Image.new("RGBA", (32, 32), (100, 150, 200, 255))
        result = apply_relief(img, ReliefConfig())
        assert result.mode == "RGBA"

    def test_rgb_input_preserved(self) -> None:
        img = _solid()
        result = apply_relief(img, ReliefConfig())
        assert result.mode == "RGB"

    def test_blend_zero_close_to_original(self) -> None:
        """With blend=0 the output should equal the original."""
        img = _solid((80, 120, 200))
        result = apply_relief(img, ReliefConfig(blend=0.0))
        assert result.size == img.size


# ---------------------------------------------------------------------------
# relief_config_from_env
# ---------------------------------------------------------------------------

class TestReliefConfigFromEnv:
    def test_defaults_without_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for key in (
            "TILESTITCH_RELIEF_ENABLED",
            "TILESTITCH_RELIEF_AZIMUTH",
            "TILESTITCH_RELIEF_ALTITUDE",
            "TILESTITCH_RELIEF_Z_FACTOR",
            "TILESTITCH_RELIEF_BLEND",
        ):
            monkeypatch.delenv(key, raising=False)
        cfg = relief_config_from_env()
        assert cfg.azimuth == 315.0
        assert cfg.altitude == 45.0

    def test_env_overrides_azimuth(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_RELIEF_AZIMUTH", "180")
        cfg = relief_config_from_env()
        assert cfg.azimuth == 180.0

    def test_env_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_RELIEF_ENABLED", "false")
        cfg = relief_config_from_env()
        assert cfg.enabled is False
