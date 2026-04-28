"""Tests for tilestitch.tile_dodge_burn."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_dodge_burn import (
    DodgeBurnConfig,
    DodgeBurnError,
    apply_dodge_burn,
    dodge_burn_config_from_env,
)


def _solid(colour: tuple[int, int, int] = (120, 120, 120), size: int = 4) -> Image.Image:
    return Image.new("RGB", (size, size), colour)


class TestDodgeBurnConfig:
    def test_defaults(self):
        cfg = DodgeBurnConfig()
        assert cfg.mode == "dodge"
        assert cfg.factor == 0.5
        assert cfg.enabled is True

    def test_mode_normalised_to_lowercase(self):
        cfg = DodgeBurnConfig(mode="DODGE")
        assert cfg.mode == "dodge"

    def test_whitespace_stripped_from_mode(self):
        cfg = DodgeBurnConfig(mode="  burn  ")
        assert cfg.mode == "burn"

    def test_burn_mode_valid(self):
        cfg = DodgeBurnConfig(mode="burn")
        assert cfg.mode == "burn"

    def test_invalid_mode_raises(self):
        with pytest.raises(DodgeBurnError, match="mode"):
            DodgeBurnConfig(mode="lighten")

    def test_factor_zero_raises(self):
        with pytest.raises(DodgeBurnError, match="factor"):
            DodgeBurnConfig(factor=0.0)

    def test_factor_negative_raises(self):
        with pytest.raises(DodgeBurnError, match="factor"):
            DodgeBurnConfig(factor=-0.1)

    def test_factor_above_one_raises(self):
        with pytest.raises(DodgeBurnError, match="factor"):
            DodgeBurnConfig(factor=1.1)

    def test_factor_one_valid(self):
        cfg = DodgeBurnConfig(factor=1.0)
        assert cfg.factor == 1.0

    def test_factor_small_positive_valid(self):
        cfg = DodgeBurnConfig(factor=0.01)
        assert cfg.factor == pytest.approx(0.01)


class TestApplyDodgeBurn:
    def test_dodge_lightens_image(self):
        img = _solid((100, 100, 100))
        cfg = DodgeBurnConfig(mode="dodge", factor=0.5)
        result = apply_dodge_burn(img, cfg)
        px = result.getpixel((0, 0))
        assert px[0] > 100

    def test_burn_darkens_image(self):
        img = _solid((200, 200, 200))
        cfg = DodgeBurnConfig(mode="burn", factor=0.5)
        result = apply_dodge_burn(img, cfg)
        px = result.getpixel((0, 0))
        assert px[0] < 200

    def test_disabled_returns_same_image(self):
        img = _solid((100, 100, 100))
        cfg = DodgeBurnConfig(enabled=False)
        result = apply_dodge_burn(img, cfg)
        assert result is img

    def test_output_mode_preserved(self):
        img = _solid().convert("RGB")
        cfg = DodgeBurnConfig(mode="dodge", factor=0.3)
        result = apply_dodge_burn(img, cfg)
        assert result.mode == "RGB"

    def test_rgba_input_preserved(self):
        img = Image.new("RGBA", (4, 4), (100, 100, 100, 200))
        cfg = DodgeBurnConfig(mode="burn", factor=0.3)
        result = apply_dodge_burn(img, cfg)
        assert result.mode == "RGBA"

    def test_dodge_full_factor_clamps_to_255(self):
        img = _solid((200, 200, 200))
        cfg = DodgeBurnConfig(mode="dodge", factor=1.0)
        result = apply_dodge_burn(img, cfg)
        px = result.getpixel((0, 0))
        assert px[0] == 255


class TestDodgeBurnConfigFromEnv:
    def test_defaults_when_env_empty(self):
        cfg = dodge_burn_config_from_env({})
        assert cfg.mode == "dodge"
        assert cfg.factor == 0.5
        assert cfg.enabled is True

    def test_reads_mode_from_env(self):
        cfg = dodge_burn_config_from_env({"TILESTITCH_DODGE_BURN_MODE": "burn"})
        assert cfg.mode == "burn"

    def test_reads_factor_from_env(self):
        cfg = dodge_burn_config_from_env({"TILESTITCH_DODGE_BURN_FACTOR": "0.25"})
        assert cfg.factor == pytest.approx(0.25)

    def test_reads_enabled_false_from_env(self):
        cfg = dodge_burn_config_from_env({"TILESTITCH_DODGE_BURN_ENABLED": "false"})
        assert cfg.enabled is False
