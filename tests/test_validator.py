"""Tests for tilestitch.validator."""

import pytest

from tilestitch.validator import (
    ValidationError,
    validate_bbox,
    validate_zoom,
)


class TestValidateZoom:
    def test_valid_zoom_returns_value(self):
        assert validate_zoom(10) == 10

    def test_zoom_zero_is_valid(self):
        assert validate_zoom(0) == 0

    def test_zoom_nineteen_is_valid(self):
        assert validate_zoom(19) == 19

    def test_negative_zoom_raises(self):
        with pytest.raises(ValidationError, match="between 0 and 19"):
            validate_zoom(-1)

    def test_zoom_above_max_raises(self):
        with pytest.raises(ValidationError, match="between 0 and 19"):
            validate_zoom(20)

    def test_float_zoom_raises(self):
        with pytest.raises(ValidationError, match="integer"):
            validate_zoom(5.0)  # type: ignore[arg-type]

    def test_string_zoom_raises(self):
        with pytest.raises(ValidationError, match="integer"):
            validate_zoom("10")  # type: ignore[arg-type]


class TestValidateBBox:
    def test_valid_bbox_returns_value(self):
        bbox = (-10.0, 40.0, 10.0, 60.0)
        assert validate_bbox(bbox) == bbox

    def test_wrong_length_raises(self):
        with pytest.raises(ValidationError, match="4 values"):
            validate_bbox((-10.0, 40.0, 10.0))  # type: ignore[arg-type]

    def test_lat_too_low_raises(self):
        with pytest.raises(ValidationError, match="Latitude"):
            validate_bbox((-10.0, -90.0, 10.0, 60.0))

    def test_lat_too_high_raises(self):
        with pytest.raises(ValidationError, match="Latitude"):
            validate_bbox((-10.0, 40.0, 10.0, 90.0))

    def test_lon_too_low_raises(self):
        with pytest.raises(ValidationError, match="Longitude"):
            validate_bbox((-181.0, 40.0, 10.0, 60.0))

    def test_lon_too_high_raises(self):
        with pytest.raises(ValidationError, match="Longitude"):
            validate_bbox((-10.0, 40.0, 181.0, 60.0))

    def test_inverted_lat_raises(self):
        with pytest.raises(ValidationError, match="min_lat"):
            validate_bbox((-10.0, 60.0, 10.0, 40.0))

    def test_equal_lat_raises(self):
        with pytest.raises(ValidationError, match="min_lat"):
            validate_bbox((-10.0, 50.0, 10.0, 50.0))

    def test_inverted_lon_raises(self):
        with pytest.raises(ValidationError, match="min_lon"):
            validate_bbox((10.0, 40.0, -10.0, 60.0))

    def test_equal_lon_raises(self):
        with pytest.raises(ValidationError, match="min_lon"):
            validate_bbox((10.0, 40.0, 10.0, 60.0))
