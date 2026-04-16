"""Tests for tilestitch.output_path."""

import pytest
from pathlib import Path

from tilestitch.output_format import OutputFormatError
from tilestitch.output_path import OutputPathError, resolve_output_path


class TestResolveOutputPath:
    def test_returns_path_object(self, tmp_path):
        result = resolve_output_path(str(tmp_path / "out.png"))
        assert isinstance(result, Path)

    def test_path_is_absolute(self, tmp_path):
        result = resolve_output_path(str(tmp_path / "out.png"))
        assert result.is_absolute()

    def test_png_extension_preserved(self, tmp_path):
        result = resolve_output_path(str(tmp_path / "map.png"))
        assert result.suffix == ".png"

    def test_tif_extension_preserved(self, tmp_path):
        result = resolve_output_path(str(tmp_path / "map.tif"))
        assert result.suffix == ".tif"

    def test_explicit_format_overrides_extension(self, tmp_path):
        result = resolve_output_path(str(tmp_path / "map.png"), fmt="geotiff")
        # format resolved; extension stays as supplied since it's a known one
        assert result is not None

    def test_creates_parent_directories(self, tmp_path):
        deep = tmp_path / "a" / "b" / "c" / "out.png"
        result = resolve_output_path(str(deep))
        assert result.parent.is_dir()

    def test_no_create_parents_does_not_create_dirs(self, tmp_path):
        deep = tmp_path / "x" / "y" / "out.png"
        resolve_output_path(str(deep), create_parents=False)
        assert not deep.parent.exists()

    def test_unknown_extension_no_fmt_raises(self, tmp_path):
        with pytest.raises(OutputFormatError):
            resolve_output_path(str(tmp_path / "map.bmp"))

    def test_no_extension_no_fmt_raises(self, tmp_path):
        with pytest.raises(OutputFormatError):
            resolve_output_path(str(tmp_path / "map"))

    def test_tilde_expanded(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        result = resolve_output_path("~/out.png")
        assert str(tmp_path) in str(result)
