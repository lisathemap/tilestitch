"""Tests for tilestitch.tile_autolevel."""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from PIL import Image

from tilestitch.tile_autolevel import (
    AutolevelConfig,
    AutolevelError,
    apply_autolevel,
    autolevel_config_from_env,
)


def _solid(r: int = 128, g: int = 64, b: int = 32, a: int = 255, size: int = 4) -> Image.Image:
    img = Image.new("RGBA", (size, size), (r, g, b, a))
    return img


# ---------------------------------------------------------------------------
# AutolevelConfig
# ---------------------------------------------------------------------------

class TestAutolevelConfig:
    def test_defaults(self) -> None:
        cfg = AutolevelConfig()
        assert cfg.enabled is True
        assert cfg.per_channel is True
        assert cfg.cutoff == 0.0

    def test_cutoff_stored(self) -> None:
        cfg = AutolevelConfig(cutoff=2.5)
        assert cfg.cutoff == 2.5

    def test_cutoff_zero_valid(self) -> None:
        cfg = AutolevelConfig(cutoff=0.0)
        assert cfg.cutoff == 0.0

    def test_cutoff_upper_boundary_invalid(self) -> None:
        with pytest.raises(AutolevelError):
            AutolevelConfig(cutoff=50.0)

    def test_negative_cutoff_raises(self) -> None:
        with pytest.raises(AutolevelError):
            AutolevelConfig(cutoff=-1.0)

    def test_invalid_enabled_raises(self) -> None:
        with pytest.raises(AutolevelError):
            AutolevelConfig(enabled="yes")  # type: ignore[arg-type]

    def test_invalid_per_channel_raises(self) -> None:
        with pytest.raises(AutolevelError):
            AutolevelConfig(per_channel=1)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# autolevel_config_from_env
# ---------------------------------------------------------------------------

class TestAutolevelConfigFromEnv:
    def test_defaults_when_no_env(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            cfg = autolevel_config_from_env()
        assert cfg.enabled is True
        assert cfg.per_channel is True
        assert cfg.cutoff == 0.0

    def test_env_disables(self) -> None:
        env = {
            "TILESTITCH_AUTOLEVEL_ENABLED": "false",
        }
        with patch.dict(os.environ, env):
            cfg = autolevel_config_from_env()
        assert cfg.enabled is False

    def test_env_cutoff(self) -> None:
        with patch.dict(os.environ, {"TILESTITCH_AUTOLEVEL_CUTOFF": "5.0"}):
            cfg = autolevel_config_from_env()
        assert cfg.cutoff == 5.0

    def test_invalid_cutoff_env_raises(self) -> None:
        with patch.dict(os.environ, {"TILESTITCH_AUTOLEVEL_CUTOFF": "bad"}):
            with pytest.raises(AutolevelError):
                autolevel_config_from_env()


# ---------------------------------------------------------------------------
# apply_autolevel
# ---------------------------------------------------------------------------

class TestApplyAutolevel:
    def test_returns_rgba_image(self) -> None:
        img = _solid()
        result = apply_autolevel(img)
        assert result.mode == "RGBA"

    def test_disabled_returns_same_object(self) -> None:
        img = _solid()
        cfg = AutolevelConfig(enabled=False)
        result = apply_autolevel(img, cfg)
        assert result is img

    def test_none_config_uses_defaults(self) -> None:
        img = _solid()
        result = apply_autolevel(img, None)
        assert result.mode == "RGBA"

    def test_per_channel_false_runs(self) -> None:
        img = _solid(100, 150, 200)
        cfg = AutolevelConfig(per_channel=False)
        result = apply_autolevel(img, cfg)
        assert result.mode == "RGBA"

    def test_alpha_preserved(self) -> None:
        img = _solid(a=200)
        result = apply_autolevel(img)
        _, _, _, a = result.split()
        pixels = list(a.getdata())
        assert all(p == 200 for p in pixels)
