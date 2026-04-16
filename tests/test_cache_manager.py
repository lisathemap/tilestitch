"""Tests for CacheManager."""
import pytest
from unittest.mock import patch, MagicMock
from tilestitch.tile_cache_config import TileCacheConfig
from tilestitch.cache_manager import CacheManager

_URL = "https://tile.example.com/10/512/384.png"
_DATA = b"PNG"


@pytest.fixture()
def cfg(tmp_path):
    return TileCacheConfig(cache_dir=tmp_path, max_size_mb=1)


@pytest.fixture()
def manager(cfg):
    return CacheManager(cfg)


class TestCacheManagerGet:
    def test_returns_none_when_disabled(self, tmp_path):
        cfg = TileCacheConfig(enabled=False, cache_dir=tmp_path)
        mgr = CacheManager(cfg)
        assert mgr.get(_URL) is None

    def test_delegates_to_cache_module(self, manager):
        with patch("tilestitch.cache_manager._cache.get_cached_tile", return_value=_DATA) as mock:
            result = manager.get(_URL)
        mock.assert_called_once()
        assert result == _DATA

    def test_returns_none_on_cache_miss(self, manager):
        with patch("tilestitch.cache_manager._cache.get_cached_tile", return_value=None):
            assert manager.get(_URL) is None


class TestCacheManagerStore:
    def test_noop_when_disabled(self, tmp_path):
        cfg = TileCacheConfig(enabled=False, cache_dir=tmp_path)
        mgr = CacheManager(cfg)
        with patch("tilestitch.cache_manager._cache.store_tile") as mock:
            mgr.store(_URL, _DATA)
        mock.assert_not_called()

    def test_delegates_to_cache_module(self, manager):
        with patch("tilestitch.cache_manager._cache.cache_size", return_value=0):
            with patch("tilestitch.cache_manager._cache.store_tile") as mock:
                manager.store(_URL, _DATA)
        mock.assert_called_once()

    def test_skips_store_when_limit_exceeded(self, tmp_path):
        cfg = TileCacheConfig(cache_dir=tmp_path, max_size_mb=1)
        mgr = CacheManager(cfg)
        big = cfg.max_size_bytes + 1
        with patch("tilestitch.cache_manager._cache.cache_size", return_value=big):
            with patch("tilestitch.cache_manager._cache.store_tile") as mock:
                mgr.store(_URL, _DATA)
        mock.assert_not_called()


class TestCacheManagerClear:
    def test_delegates_clear(self, manager):
        with patch("tilestitch.cache_manager._cache.clear_cache") as mock:
            manager.clear()
        mock.assert_called_once()


class TestCacheManagerSize:
    def test_returns_integer(self, manager):
        with patch("tilestitch.cache_manager._cache.cache_size", return_value=42):
            assert manager.size() == 42
