"""Tests for tilestitch.bounds_parser."""

import pytest

from tilestitch.bounds_parser import BBoxParseError, bbox_to_str, parse_bbox


class TestParseBbox:
    def test_valid_string_returns_tuple(self):
        result = parse_bbox("-1.0,51.0,1.0,52.0")
        assert result == (-1.0, 51.0, 1.0, 52.0)

    def test_returns_floats(self):
        result = parse_bbox("0,0,1,1")
        assert all(isinstance(v, float) for v in result)

    def test_whitespace_around_values_is_tolerated(self):
        result = parse_bbox(" -10.5 , 40.0 , 10.5 , 50.0 ")
        assert result == (-10.5, 40.0, 10.5, 50.0)

    def test_too_few_parts_raises(self):
        with pytest.raises(BBoxParseError, match="Expected 4"):
            parse_bbox("1.0,2.0,3.0")

    def test_too_many_parts_raises(self):
        with pytest.raises(BBoxParseError, match="Expected 4"):
            parse_bbox("1.0,2.0,3.0,4.0,5.0")

    def test_non_numeric_value_raises(self):
        with pytest.raises(BBoxParseError, match="Non-numeric"):
            parse_bbox("a,b,c,d")

    def test_min_lon_equals_max_lon_raises(self):
        with pytest.raises(BBoxParseError, match="min_lon"):
            parse_bbox("10.0,40.0,10.0,50.0")

    def test_min_lat_equals_max_lat_raises(self):
        with pytest.raises(BBoxParseError, match="min_lat"):
            parse_bbox("0.0,45.0,1.0,45.0")

    def test_min_lon_greater_than_max_lon_raises(self):
        with pytest.raises(BBoxParseError):
            parse_bbox("20.0,40.0,10.0,50.0")

    def test_min_lat_greater_than_max_lat_raises(self):
        with pytest.raises(BBoxParseError):
            parse_bbox("0.0,55.0,1.0,45.0")

    def test_longitude_out_of_range_raises(self):
        with pytest.raises(BBoxParseError, match="Longitude"):
            parse_bbox("-200.0,40.0,-100.0,50.0")

    def test_latitude_out_of_range_raises(self):
        with pytest.raises(BBoxParseError, match="Latitude"):
            parse_bbox("0.0,-100.0,1.0,50.0")

    def test_extreme_valid_values(self):
        result = parse_bbox("-180.0,-90.0,180.0,90.0")
        assert result == (-180.0, -90.0, 180.0, 90.0)


class TestBboxToStr:
    def test_round_trips_through_parse(self):
        original = "-1.5,51.0,1.5,52.0"
        assert bbox_to_str(parse_bbox(original)) == original

    def test_formats_integers_without_decimals(self):
        result = bbox_to_str((0.0, 0.0, 1.0, 1.0))
        assert result == "0.0,0.0,1.0,1.0"
