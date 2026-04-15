"""Tests for tilestitch.cache."""

import pytest
from pathlib import Path

from tilestitch.cache import (
    _tile_cache_path,
    get_cached_tile,
    store_tile,
    clear_cache,
    cache_size,
)

SAMPLE_URL = "https://tile.openstreetmap.org/10/512/384.png"
SAMPLE_DATA = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


class TestTileCachePath:
    def test_returns_path_object(self, tmp_path):
        result = _tile_cache_path(tmp_path, SAMPLE_URL)
        assert isinstance(result, Path)

    def test_path_inside_cache_dir(self, tmp_path):
        result = _tile_cache_path(tmp_path, SAMPLE_URL)
        assert result.is_relative_to(tmp_path)

    def test_different_urls_produce_different_paths(self, tmp_path):
        url2 = "https://tile.openstreetmap.org/10/512/385.png"
        assert _tile_cache_path(tmp_path, SAMPLE_URL) != _tile_cache_path(tmp_path, url2)

    def test_same_url_produces_same_path(self, tmp_path):
        assert _tile_cache_path(tmp_path, SAMPLE_URL) == _tile_cache_path(tmp_path, SAMPLE_URL)

    def test_uses_two_level_sharding(self, tmp_path):
        path = _tile_cache_path(tmp_path, SAMPLE_URL)
        # parent = shard2, grandparent = shard1, great-grandparent = cache_dir
        assert path.parent.parent.parent == tmp_path


class TestGetCachedTile:
    def test_returns_none_when_not_cached(self, tmp_path):
        assert get_cached_tile(SAMPLE_URL, cache_dir=tmp_path) is None

    def test_returns_data_after_store(self, tmp_path):
        store_tile(SAMPLE_URL, SAMPLE_DATA, cache_dir=tmp_path)
        result = get_cached_tile(SAMPLE_URL, cache_dir=tmp_path)
        assert result == SAMPLE_DATA


class TestStoreTile:
    def test_creates_file(self, tmp_path):
        path = store_tile(SAMPLE_URL, SAMPLE_DATA, cache_dir=tmp_path)
        assert path.exists()

    def test_returns_path(self, tmp_path):
        path = store_tile(SAMPLE_URL, SAMPLE_DATA, cache_dir=tmp_path)
        assert isinstance(path, Path)

    def test_file_content_matches(self, tmp_path):
        path = store_tile(SAMPLE_URL, SAMPLE_DATA, cache_dir=tmp_path)
        assert path.read_bytes() == SAMPLE_DATA

    def test_overwrites_existing(self, tmp_path):
        store_tile(SAMPLE_URL, SAMPLE_DATA, cache_dir=tmp_path)
        new_data = b"new content"
        store_tile(SAMPLE_URL, new_data, cache_dir=tmp_path)
        assert get_cached_tile(SAMPLE_URL, cache_dir=tmp_path) == new_data


class TestClearCache:
    def test_returns_zero_on_empty_dir(self, tmp_path):
        assert clear_cache(cache_dir=tmp_path) == 0

    def test_returns_count_of_removed_files(self, tmp_path):
        store_tile(SAMPLE_URL, SAMPLE_DATA, cache_dir=tmp_path)
        store_tile(SAMPLE_URL + "2", SAMPLE_DATA, cache_dir=tmp_path)
        removed = clear_cache(cache_dir=tmp_path)
        assert removed == 2

    def test_cache_empty_after_clear(self, tmp_path):
        store_tile(SAMPLE_URL, SAMPLE_DATA, cache_dir=tmp_path)
        clear_cache(cache_dir=tmp_path)
        assert get_cached_tile(SAMPLE_URL, cache_dir=tmp_path) is None


class TestCacheSize:
    def test_returns_zero_when_no_cache_dir(self, tmp_path):
        missing = tmp_path / "nonexistent"
        assert cache_size(cache_dir=missing) == 0

    def test_returns_correct_size(self, tmp_path):
        store_tile(SAMPLE_URL, SAMPLE_DATA, cache_dir=tmp_path)
        assert cache_size(cache_dir=tmp_path) == len(SAMPLE_DATA)
