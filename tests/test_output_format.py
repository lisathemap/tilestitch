"""Tests for tilestitch.output_format."""

import pytest

from tilestitch.output_format import (
    OutputFormat,
    OutputFormatError,
    resolve_format,
)


class TestOutputFormatFromString:
    def test_png_lowercase(self):
        assert OutputFormat.from_string("png") == OutputFormat.PNG

    def test_geotiff_lowercase(self):
        assert OutputFormat.from_string("geotiff") == OutputFormat.GEOTIFF

    def test_case_insensitive(self):
        assert OutputFormat.from_string("PNG") == OutputFormat.PNG
        assert OutputFormat.from_string("GeoTIFF") == OutputFormat.GEOTIFF

    def test_whitespace_stripped(self):
        assert OutputFormat.from_string("  png  ") == OutputFormat.PNG

    def test_unknown_raises(self):
        with pytest.raises(OutputFormatError, match="Unsupported output format"):
            OutputFormat.from_string("jpeg")


class TestOutputFormatProperties:
    def test_png_extension(self):
        assert OutputFormat.PNG.extension == "png"

    def test_geotiff_extension(self):
        assert OutputFormat.GEOTIFF.extension == "tif"

    def test_png_mime(self):
        assert OutputFormat.PNG.mime_type == "image/png"

    def test_geotiff_mime(self):
        assert OutputFormat.GEOTIFF.mime_type == "image/tiff"


class TestResolveFormat:
    def test_explicit_format_takes_precedence(self):
        result = resolve_format("output.png", fmt="geotiff")
        assert result == OutputFormat.GEOTIFF

    def test_infer_png_from_extension(self):
        assert resolve_format("map.png") == OutputFormat.PNG

    def test_infer_tif_from_extension(self):
        assert resolve_format("map.tif") == OutputFormat.GEOTIFF

    def test_infer_tiff_from_extension(self):
        assert resolve_format("map.tiff") == OutputFormat.GEOTIFF

    def test_no_extension_no_fmt_raises(self):
        with pytest.raises(OutputFormatError, match="Cannot infer output format"):
            resolve_format("output")

    def test_unknown_extension_raises(self):
        with pytest.raises(OutputFormatError):
            resolve_format("output.bmp")

    def test_explicit_fmt_overrides_unknown_extension(self):
        result = resolve_format("output.bmp", fmt="png")
        assert result == OutputFormat.PNG
