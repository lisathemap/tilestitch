"""Tests for tilestitch.tile_gamma."""
from __future__ import annotations

import os

import pytest
from PIL import Image

from tilestitch.tile_gamma import (
    GammaConfig,
    GammaError,
    apply_gamma,
    gamma_config_from_env,
)


def _solid(colour: tuple[int, ...], mode: str = "RGB", size: tuple[int, int] = (4, 4)) -> Image.Image:
    img = Image.new(mode, size, colour)
    return img


class TestGammaConfig:
    def test_defaults(self):
        cfg = GammaConfig()
        assert cfg.gamma == 1.0
        assert cfg.enabled is True

    def test_gamma_stored(self):
        cfg = GammaConfig(gamma=2.2)
        assert cfg.gamma == 2.2

    def test_zero_gamma_raises(self):
        with pytest.raises(GammaError):
            GammaConfig(gamma=0.0)

    def test_negative_gamma_raises(self):
        with pytest.raises(GammaError):
            GammaConfig(gamma=-1.0)

    def test_positive_gamma_valid(self):
        cfg = GammaConfig(gamma=0.5)
        assert cfg.gamma == 0.5


class TestApplyGamma:
    def test_identity_gamma_returns_equal_image(self):
        img = _solid((100, 150, 200))
        result = apply_gamma(img, GammaConfig(gamma=1.0))
        assert list(result.getdata()) == list(img.getdata())

    def test_disabled_returns_same_image(self):
        img = _solid((100, 150, 200))
        result = apply_gamma(img, GammaConfig(enabled=False, gamma=2.2))
        assert result is img

    def test_brightens_with_gamma_less_than_one(self):
        img = _solid((100, 100, 100))
        result = apply_gamma(img, GammaConfig(gamma=0.5))
        r, g, b = result.getpixel((0, 0))
        assert r > 100

    def test_darkens_with_gamma_greater_than_one(self):
        img = _solid((200, 200, 200))
        result = apply_gamma(img, GammaConfig(gamma=2.0))
        r, g, b = result.getpixel((0, 0))
        assert r < 200

    def test_rgba_alpha_preserved(self):
        img = _solid((100, 100, 100, 128), mode="RGBA")
        result = apply_gamma(img, GammaConfig(gamma=2.0))
        assert result.mode == "RGBA"
        assert result.getpixel((0, 0))[3] == 128

    def test_output_mode_matches_input(self):
        img = _solid((80, 120, 200))
        result = apply_gamma(img, GammaConfig(gamma=1.8))
        assert result.mode == "RGB"


class TestGammaConfigFromEnv:
    def test_defaults_when_env_unset(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_GAMMA", raising=False)
        monkeypatch.delenv("TILESTITCH_GAMMA_ENABLED", raising=False)
        cfg = gamma_config_from_env()
        assert cfg.gamma == 1.0
        assert cfg.enabled is True

    def test_reads_gamma_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_GAMMA", "2.2")
        cfg = gamma_config_from_env()
        assert cfg.gamma == pytest.approx(2.2)

    def test_disabled_via_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_GAMMA_ENABLED", "false")
        cfg = gamma_config_from_env()
        assert cfg.enabled is False

    def test_invalid_gamma_env_raises(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_GAMMA", "not_a_number")
        with pytest.raises(GammaError):
            gamma_config_from_env()
