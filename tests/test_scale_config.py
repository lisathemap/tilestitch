"""Tests for tilestitch.scale_config."""

import pytest

from tilestitch.scale_config import ScaleConfig, scale_config_from_env
from tilestitch.tile_scaler import ScaleMethod


class TestScaleConfig:
    def test_stores_tile_size(self):
        cfg = ScaleConfig(tile_size=512, scale_factor=1.0, method=ScaleMethod.LANCZOS)
        assert cfg.tile_size == 512

    def test_stores_scale_factor(self):
        cfg = ScaleConfig(tile_size=256, scale_factor=2.5, method=ScaleMethod.BICUBIC)
        assert cfg.scale_factor == 2.5

    def test_stores_method(self):
        cfg = ScaleConfig(tile_size=256, scale_factor=1.0, method=ScaleMethod.NEAREST)
        assert cfg.method is ScaleMethod.NEAREST

    def test_zero_tile_size_raises(self):
        with pytest.raises(ValueError):
            ScaleConfig(tile_size=0, scale_factor=1.0, method=ScaleMethod.LANCZOS)

    def test_negative_tile_size_raises(self):
        with pytest.raises(ValueError):
            ScaleConfig(tile_size=-256, scale_factor=1.0, method=ScaleMethod.LANCZOS)

    def test_zero_scale_factor_raises(self):
        with pytest.raises(ValueError):
            ScaleConfig(tile_size=256, scale_factor=0.0, method=ScaleMethod.LANCZOS)

    def test_is_frozen(self):
        cfg = ScaleConfig(tile_size=256, scale_factor=1.0, method=ScaleMethod.LANCZOS)
        with pytest.raises(Exception):
            cfg.tile_size = 512  # type: ignore[misc]


class TestScaleConfigFromEnv:
    def test_defaults_applied(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_TILE_SIZE", raising=False)
        monkeypatch.delenv("TILESTITCH_SCALE", raising=False)
        monkeypatch.delenv("TILESTITCH_SCALE_METHOD", raising=False)
        cfg = scale_config_from_env()
        assert cfg.tile_size == 256
        assert cfg.scale_factor == 1.0
        assert cfg.method is ScaleMethod.LANCZOS

    def test_tile_size_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_TILE_SIZE", "512")
        cfg = scale_config_from_env()
        assert cfg.tile_size == 512

    def test_scale_factor_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SCALE", "2.0")
        cfg = scale_config_from_env()
        assert cfg.scale_factor == 2.0

    def test_method_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SCALE_METHOD", "nearest")
        cfg = scale_config_from_env()
        assert cfg.method is ScaleMethod.NEAREST

    def test_invalid_method_falls_back_to_default(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SCALE_METHOD", "not_a_method")
        cfg = scale_config_from_env()
        assert cfg.method is ScaleMethod.LANCZOS
