"""Tests for the CLI argument parsing and entry point."""

from unittest.mock import MagicMock, patch

import pytest

from tilestitch.cli import build_parser, main


class TestBuildParser:
    def test_returns_parser(self):
        parser = build_parser()
        assert parser is not None

    def test_required_bbox(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--zoom", "10"])

    def test_required_zoom(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--bbox", "51.0", "-1.0", "52.0", "0.0"])

    def test_parses_bbox_as_floats(self):
        parser = build_parser()
        args = parser.parse_args(["--bbox", "51.0", "-1.0", "52.0", "0.0", "--zoom", "10"])
        assert args.bbox == [51.0, -1.0, 52.0, 0.0]

    def test_default_source_is_osm(self):
        parser = build_parser()
        args = parser.parse_args(["--bbox", "51.0", "-1.0", "52.0", "0.0", "--zoom", "10"])
        assert args.source == "osm"

    def test_default_output_is_png(self):
        parser = build_parser()
        args = parser.parse_args(["--bbox", "51.0", "-1.0", "52.0", "0.0", "--zoom", "10"])
        assert args.output == "output.png"

    def test_default_concurrency(self):
        parser = build_parser()
        args = parser.parse_args(["--bbox", "51.0", "-1.0", "52.0", "0.0", "--zoom", "10"])
        assert args.concurrency == 8

    def test_custom_source(self):
        parser = build_parser()
        args = parser.parse_args(["--bbox", "51.0", "-1.0", "52.0", "0.0", "--zoom", "10", "--source", "stamen"])
        assert args.source == "stamen"

    def test_custom_output(self):
        parser = build_parser()
        args = parser.parse_args(["--bbox", "51.0", "-1.0", "52.0", "0.0", "--zoom", "10", "--output", "map.png"])
        assert args.output == "map.png"

    def test_custom_concurrency(self):
        parser = build_parser()
        args = parser.parse_args(["--bbox", "51.0", "-1.0", "52.0", "0.0", "--zoom", "10", "--concurrency", "4"])
        assert args.concurrency == 4


class TestMain:
    _base_argv = ["--bbox", "51.0", "-1.0", "52.0", "0.0", "--zoom", "10"]

    def test_list_sources_exits_zero(self):
        with patch("tilestitch.cli.list_sources", return_value=[("osm", "OpenStreetMap")]) as mock_ls:
            result = main(["--list-sources"])
        mock_ls.assert_called_once()
        assert result == 0

    def test_invalid_bbox_min_lat_gte_max_lat(self):
        result = main(["--bbox", "52.0", "-1.0", "51.0", "0.0", "--zoom", "10"])
        assert result == 1

    def test_invalid_bbox_min_lon_gte_max_lon(self):
        result = main(["--bbox", "51.0", "1.0", "52.0", "0.0", "--zoom", "10"])
        assert result == 1

    def test_invalid_zoom_too_high(self):
        result = main(["--bbox", "51.0", "-1.0", "52.0", "0.0", "--zoom", "20"])
        assert result == 1

    def test_invalid_zoom_negative(self):
        result = main(["--bbox", "51.0", "-1.0", "52.0", "0.0", "--zoom", "-1"])
        assert result == 1

    def test_calls_run_with_correct_args(self):
        with patch("tilestitch.cli.run") as mock_run:
            result = main(self._base_argv)
        mock_run.assert_called_once_with(
            bbox=(51.0, -1.0, 52.0, 0.0),
            zoom=10,
            source="osm",
            output="output.png",
            concurrency=8,
        )
        assert result == 0

    def test_calls_run_with_custom_args(self):
        argv = ["--bbox", "51.0", "-1.0", "52.0", "0.0", "--zoom", "12", "--source", "stamen", "--output", "map.png", "--concurrency", "4"]
        with patch("tilestitch.cli.run") as mock_run:
            result = main(argv)
        mock_run.assert_called_once_with(
            bbox=(51.0, -1.0, 52.0, 0.0),
            zoom=12,
            source="stamen",
            output="map.png",
            concurrency=4,
        )
        assert result == 0

    def test_run_exception_returns_one(self):
        with patch("tilestitch.cli.run", side_effect=ValueError("bad source")):
            result = main(self._base_argv)
        assert result
