"""Tests for tilestitch.compositor_config."""
from __future__ import annotations

import pytest

from tilestitch.compositor_config import CompositorConfig, compositor_config_from_env


class TestCompositorConfig:
    def test_defaults(self):
        cfg = CompositorConfig()
        assert cfg.background == (0, 0, 0, 0)
        assert cfg.default_opacity == 1.0
        assert cfg.auto_size is True

    def test_invalid_opacity_raises(self):
        with pytest.raises(ValueError):
            CompositorConfig(default_opacity=1.5)

    def test_opacity_zero_valid(self):
        cfg = CompositorConfig(default_opacity=0.0)
        assert cfg.default_opacity == 0.0

    def test_invalid_background_raises(self):
        with pytest.raises(ValueError):
            CompositorConfig(background=(0, 0, 0))  # type: ignore[arg-type]

    def test_custom_background(self):
        cfg = CompositorConfig(background=(255, 255, 255, 128))
        assert cfg.background == (255, 255, 255, 128)


class TestCompositorConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        for key in ("TILESTITCH_COMPOSITOR_OPACITY", "TILESTITCH_COMPOSITOR_AUTO_SIZE", "TILESTITCH_COMPOSITOR_BG"):
            monkeypatch.delenv(key, raising=False)
        cfg = compositor_config_from_env()
        assert cfg.default_opacity == 1.0
        assert cfg.auto_size is True

    def test_opacity_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_COMPOSITOR_OPACITY", "0.75")
        cfg = compositor_config_from_env()
        assert cfg.default_opacity == 0.75

    def test_auto_size_false_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_COMPOSITOR_AUTO_SIZE", "false")
        cfg = compositor_config_from_env()
        assert cfg.auto_size is False

    def test_bg_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_COMPOSITOR_BG", "10,20,30,40")
        cfg = compositor_config_from_env()
        assert cfg.background == (10, 20, 30, 40)
