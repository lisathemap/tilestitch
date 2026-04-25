"""Tests for tilestitch.tile_shear."""
from __future__ import annotations

import os

import pytest
from PIL import Image

from tilestitch.tile_shear import (
    ShearConfig,
    ShearError,
    apply_shear,
    shear_config_from_env,
)


def _solid(colour: tuple[int, int, int] = (100, 150, 200), size: int = 64) -> Image.Image:
    img = Image.new("RGB", (size, size), colour)
    return img


# ---------------------------------------------------------------------------
# ShearConfig
# ---------------------------------------------------------------------------

class TestShearConfig:
    def test_defaults(self) -> None:
        cfg = ShearConfig()
        assert cfg.x_shear == 0.0
        assert cfg.y_shear == 0.0
        assert cfg.enabled is True
        assert cfg.fill_colour == (0, 0, 0, 0)

    def test_x_shear_stored(self) -> None:
        cfg = ShearConfig(x_shear=0.3)
        assert cfg.x_shear == 0.3

    def test_y_shear_stored(self) -> None:
        cfg = ShearConfig(y_shear=-0.5)
        assert cfg.y_shear == -0.5

    def test_x_shear_above_one_raises(self) -> None:
        with pytest.raises(ShearError):
            ShearConfig(x_shear=1.1)

    def test_x_shear_below_minus_one_raises(self) -> None:
        with pytest.raises(ShearError):
            ShearConfig(x_shear=-1.1)

    def test_y_shear_above_one_raises(self) -> None:
        with pytest.raises(ShearError):
            ShearConfig(y_shear=1.01)

    def test_y_shear_below_minus_one_raises(self) -> None:
        with pytest.raises(ShearError):
            ShearConfig(y_shear=-1.5)

    def test_boundary_values_valid(self) -> None:
        cfg = ShearConfig(x_shear=1.0, y_shear=-1.0)
        assert cfg.x_shear == 1.0
        assert cfg.y_shear == -1.0

    def test_disabled_stored(self) -> None:
        cfg = ShearConfig(enabled=False)
        assert cfg.enabled is False


# ---------------------------------------------------------------------------
# apply_shear
# ---------------------------------------------------------------------------

class TestApplyShear:
    def test_returns_image(self) -> None:
        img = _solid()
        cfg = ShearConfig(x_shear=0.2)
        result = apply_shear(img, cfg)
        assert isinstance(result, Image.Image)

    def test_no_shear_returns_same_object(self) -> None:
        img = _solid()
        cfg = ShearConfig(x_shear=0.0, y_shear=0.0)
        result = apply_shear(img, cfg)
        assert result is img

    def test_disabled_returns_same_object(self) -> None:
        img = _solid()
        cfg = ShearConfig(x_shear=0.5, enabled=False)
        result = apply_shear(img, cfg)
        assert result is img

    def test_x_shear_widens_canvas(self) -> None:
        img = _solid(size=64)
        cfg = ShearConfig(x_shear=0.5)
        result = apply_shear(img, cfg)
        assert result.width > img.width

    def test_y_shear_tallens_canvas(self) -> None:
        img = _solid(size=64)
        cfg = ShearConfig(y_shear=0.5)
        result = apply_shear(img, cfg)
        assert result.height > img.height

    def test_output_mode_is_rgba(self) -> None:
        img = _solid()
        cfg = ShearConfig(x_shear=0.3)
        result = apply_shear(img, cfg)
        assert result.mode == "RGBA"


# ---------------------------------------------------------------------------
# shear_config_from_env
# ---------------------------------------------------------------------------

class TestShearConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for key in ("TILESTITCH_SHEAR_X", "TILESTITCH_SHEAR_Y",
                    "TILESTITCH_SHEAR_ENABLED", "TILESTITCH_SHEAR_FILL"):
            monkeypatch.delenv(key, raising=False)
        cfg = shear_config_from_env()
        assert cfg.x_shear == 0.0
        assert cfg.y_shear == 0.0
        assert cfg.enabled is True

    def test_reads_x_and_y(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_SHEAR_X", "0.25")
        monkeypatch.setenv("TILESTITCH_SHEAR_Y", "-0.1")
        monkeypatch.delenv("TILESTITCH_SHEAR_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_SHEAR_FILL", raising=False)
        cfg = shear_config_from_env()
        assert cfg.x_shear == pytest.approx(0.25)
        assert cfg.y_shear == pytest.approx(-0.1)

    def test_disabled_via_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_SHEAR_ENABLED", "false")
        monkeypatch.delenv("TILESTITCH_SHEAR_X", raising=False)
        monkeypatch.delenv("TILESTITCH_SHEAR_Y", raising=False)
        monkeypatch.delenv("TILESTITCH_SHEAR_FILL", raising=False)
        cfg = shear_config_from_env()
        assert cfg.enabled is False

    def test_invalid_fill_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_SHEAR_FILL", "0,0,0")
        monkeypatch.delenv("TILESTITCH_SHEAR_X", raising=False)
        monkeypatch.delenv("TILESTITCH_SHEAR_Y", raising=False)
        monkeypatch.delenv("TILESTITCH_SHEAR_ENABLED", raising=False)
        with pytest.raises(ShearError):
            shear_config_from_env()
