"""Tests for tilestitch.metadata."""

import json
import os
import tempfile

import pytest

from tilestitch.metadata import (
    ImageMetadata,
    build_metadata,
    save_metadata,
)
from tilestitch.tile_math import TileBounds


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bounds(x_min=10, y_min=20, x_max=11, y_max=21) -> TileBounds:
    return TileBounds(x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max)


def _sample_metadata(**kwargs) -> ImageMetadata:
    defaults = dict(
        source="osm",
        zoom=10,
        bbox=(51.0, -0.5, 51.5, 0.5),
        bounds=_bounds(),
        image_width=512,
        image_height=512,
    )
    defaults.update(kwargs)
    return build_metadata(**defaults)


# ---------------------------------------------------------------------------
# build_metadata
# ---------------------------------------------------------------------------

class TestBuildMetadata:
    def test_returns_image_metadata_instance(self):
        meta = _sample_metadata()
        assert isinstance(meta, ImageMetadata)

    def test_source_stored(self):
        meta = _sample_metadata(source="stamen")
        assert meta.source == "stamen"

    def test_zoom_stored(self):
        meta = _sample_metadata(zoom=14)
        assert meta.zoom == 14

    def test_bbox_stored(self):
        bbox = (48.0, 2.0, 49.0, 3.0)
        meta = _sample_metadata(bbox=bbox)
        assert meta.bbox == bbox

    def test_tile_count_2x2(self):
        # x: 10-11 => 2 tiles, y: 20-21 => 2 tiles => 4 total
        meta = _sample_metadata(bounds=_bounds(10, 20, 11, 21))
        assert meta.tile_count == 4

    def test_tile_count_single(self):
        meta = _sample_metadata(bounds=_bounds(5, 5, 5, 5))
        assert meta.tile_count == 1

    def test_image_dimensions(self):
        meta = _sample_metadata(image_width=1024, image_height=768)
        assert meta.image_width == 1024
        assert meta.image_height == 768

    def test_default_crs(self):
        meta = _sample_metadata()
        assert meta.crs == "EPSG:4326"

    def test_tile_bounds_tuple(self):
        meta = _sample_metadata(bounds=_bounds(1, 2, 3, 4))
        assert meta.tile_bounds == (1, 2, 3, 4)


# ---------------------------------------------------------------------------
# to_dict / to_json
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_to_dict_returns_dict(self):
        assert isinstance(_sample_metadata().to_dict(), dict)

    def test_to_dict_contains_source(self):
        d = _sample_metadata(source="osm").to_dict()
        assert d["source"] == "osm"

    def test_to_json_is_valid_json(self):
        j = _sample_metadata().to_json()
        parsed = json.loads(j)
        assert isinstance(parsed, dict)

    def test_to_json_contains_zoom(self):
        j = _sample_metadata(zoom=7).to_json()
        assert json.loads(j)["zoom"] == 7


# ---------------------------------------------------------------------------
# save_metadata
# ---------------------------------------------------------------------------

class TestSaveMetadata:
    def test_creates_file(self):
        meta = _sample_metadata()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "meta.json")
            save_metadata(meta, path)
            assert os.path.exists(path)

    def test_file_content_is_valid_json(self):
        meta = _sample_metadata()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "meta.json")
            save_metadata(meta, path)
            with open(path) as fh:
                data = json.load(fh)
            assert data["source"] == meta.source
            assert data["zoom"] == meta.zoom
