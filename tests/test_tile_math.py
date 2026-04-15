"""Tests for tilestitch.tile_math coordinate utilities."""

import pytest
from tilestitch.tile_math import (
    lat_lon_to_tile,
    tile_to_lat_lon,
    tile_bounds,
    tiles_for_bbox,
    TileBounds,
)


class TestLatLonToTile:
    def test_known_location_zoom10(self):
        # Berlin, roughly tile (549, 335) at zoom 10
        x, y = lat_lon_to_tile(52.52, 13.405, 10)
        assert x == 549
        assert y == 335

    def test_zoom0_always_returns_origin(self):
        x, y = lat_lon_to_tile(0.0, 0.0, 0)
        assert x == 0 and y == 0

    def test_invalid_latitude_raises(self):
        with pytest.raises(ValueError, match="Latitude"):
            lat_lon_to_tile(91.0, 0.0, 5)

    def test_invalid_longitude_raises(self):
        with pytest.raises(ValueError, match="Longitude"):
            lat_lon_to_tile(0.0, 181.0, 5)

    def test_invalid_zoom_raises(self):
        with pytest.raises(ValueError, match="Zoom"):
            lat_lon_to_tile(0.0, 0.0, 23)


class TestTileToLatLon:
    def test_nw_corner_of_world_tile_zoom0(self):
        lat, lon = tile_to_lat_lon(0, 0, 0)
        assert lon == pytest.approx(-180.0)
        assert lat == pytest.approx(85.0511, abs=0.001)

    def test_roundtrip(self):
        original_lat, original_lon = 48.8566, 2.3522  # Paris
        zoom = 12
        x, y = lat_lon_to_tile(original_lat, original_lon, zoom)
        nw_lat, nw_lon = tile_to_lat_lon(x, y, zoom)
        se_lat, se_lon = tile_to_lat_lon(x + 1, y + 1, zoom)
        # Original point should fall within the tile bounds
        assert nw_lon <= original_lon <= se_lon
        assert se_lat <= original_lat <= nw_lat


class TestTileBounds:
    def test_returns_tile_bounds_instance(self):
        bounds = tile_bounds(0, 0, 0)
        assert isinstance(bounds, TileBounds)

    def test_bounds_cover_full_world_at_zoom0(self):
        bounds = tile_bounds(0, 0, 0)
        assert bounds.min_lon == pytest.approx(-180.0)
        assert bounds.max_lon == pytest.approx(180.0)
        assert bounds.max_lat == pytest.approx(85.0511, abs=0.001)


class TestTilesForBbox:
    def test_single_tile_bbox(self):
        # Bbox entirely within one tile
        bounds = tile_bounds(549, 335, 10)
        tiles = tiles_for_bbox(
            bounds.min_lon + 0.001,
            bounds.min_lat + 0.001,
            bounds.max_lon - 0.001,
            bounds.max_lat - 0.001,
            zoom=10,
        )
        assert (549, 335) in tiles
        assert len(tiles) == 1

    def test_returns_list_of_tuples(self):
        tiles = tiles_for_bbox(-0.1, 51.4, 0.1, 51.6, zoom=12)
        assert isinstance(tiles, list)
        assert all(isinstance(t, tuple) and len(t) == 2 for t in tiles)

    def test_larger_area_returns_multiple_tiles(self):
        tiles = tiles_for_bbox(-5.0, 48.0, 10.0, 55.0, zoom=6)
        assert len(tiles) > 1
