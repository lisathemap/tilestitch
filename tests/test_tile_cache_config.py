"""Tests for TileCacheConfig and tile_cache_config_from_env."""
import pytest
from pathlib import Path
from tilestitch.tile_cache_config import (
    TileCacheConfig,
    tile_cache_config_from_env,
    _DEFAULT_CACHE_DIR,
    _DEFAULT_MAX_SIZE_MB,
)


class TestTileCacheConfig:
    def test_defaults(self):
        cfg = TileCacheConfig()
        assert cfg.enabled is True
        assert cfg.cache_dir == _DEFAULT_CACHE_DIR
        assert cfg.max_size_mb == _DEFAULT_MAX_SIZE_MB

    def test_max_size_bytes(self):
        cfg = TileCacheConfig(max_size_mb=1)
        assert cfg.max_size_bytes == 1024 * 1024

    def test_string_cache_dir_converted_to_path(self):
        cfg = TileCacheConfig(cache_dir="/tmp/tiles")
        assert isinstance(cfg.cache_dir, Path)
        assert cfg.cache_dir == Path("/tmp/tiles")

    def test_zero_max_size_raises(self):
        with pytest.raises(ValueError):
            TileCacheConfig(max_size_mb=0)

    def test_negative_max_size_raises(self):
        with pytest.raises(ValueError):
            TileCacheConfig(max_size_mb=-10)

    def test_disabled(self):
        cfg = TileCacheConfig(enabled=False)
        assert cfg.enabled is False


class TestTileCacheConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_CACHE_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_CACHE_DIR", raising=False)
        monkeypatch.delenv("TILESTITCH_CACHE_MAX_SIZE_MB", raising=False)
        cfg = tile_cache_config_from_env()
        assert cfg.enabled is True
        assert cfg.max_size_mb == _DEFAULT_MAX_SIZE_MB

    def test_disabled_via_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_CACHE_ENABLED", "false")
        cfg = tile_cache_config_from_env()
        assert cfg.enabled is False

    def test_custom_dir_via_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_CACHE_DIR", "/tmp/custom")
        cfg = tile_cache_config_from_env()
        assert cfg.cache_dir == Path("/tmp/custom")

    def test_custom_max_size_via_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_CACHE_MAX_SIZE_MB", "128")
        cfg = tile_cache_config_from_env()
        assert cfg.max_size_mb == 128

    def test_invalid_max_size_falls_back_to_default(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_CACHE_MAX_SIZE_MB", "notanumber")
        cfg = tile_cache_config_from_env()
        assert cfg.max_size_mb == _DEFAULT_MAX_SIZE_MB
