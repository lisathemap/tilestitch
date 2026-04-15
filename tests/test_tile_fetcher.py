"""Tests for tile_fetcher module."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from tilestitch.tile_fetcher import fetch_tile, fetch_tiles, _build_session
from tilestitch.tile_math import TileBounds

OSM_TEMPLATE = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"


class TestBuildSession:
    def test_returns_session(self):
        session = _build_session()
        assert isinstance(session, requests.Session)

    def test_user_agent_set(self):
        session = _build_session()
        assert "tilestitch" in session.headers["User-Agent"]


class TestFetchTile:
    def test_calls_correct_url(self):
        mock_response = MagicMock()
        mock_response.content = b"PNG_DATA"
        mock_response.raise_for_status = MagicMock()

        with patch("tilestitch.tile_fetcher.requests.Session") as MockSession:
            mock_session = MockSession.return_value
            mock_session.get.return_value = mock_response

            result = fetch_tile(OSM_TEMPLATE, x=1, y=2, zoom=3)

        called_url = mock_session.get.call_args[0][0]
        assert "/3/1/2.png" in called_url
        assert result == b"PNG_DATA"

    def test_raises_on_http_error(self):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404")

        with patch("tilestitch.tile_fetcher.requests.Session") as MockSession:
            mock_session = MockSession.return_value
            mock_session.get.return_value = mock_response

            with pytest.raises(requests.HTTPError):
                fetch_tile(OSM_TEMPLATE, x=0, y=0, zoom=0)

    def test_uses_provided_session(self):
        mock_response = MagicMock()
        mock_response.content = b"TILE"
        mock_response.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        result = fetch_tile(OSM_TEMPLATE, x=5, y=5, zoom=5, session=mock_session)
        assert mock_session.get.called
        assert result == b"TILE"


class TestFetchTiles:
    def _make_bounds(self):
        return TileBounds(x_min=0, x_max=1, y_min=0, y_max=1, zoom=2)

    def test_returns_all_tiles(self):
        mock_response = MagicMock()
        mock_response.content = b"IMG"
        mock_response.raise_for_status = MagicMock()

        with patch("tilestitch.tile_fetcher._build_session") as mock_build:
            mock_session = MagicMock()
            mock_session.get.return_value = mock_response
            mock_build.return_value = mock_session

            bounds = self._make_bounds()
            results = fetch_tiles(OSM_TEMPLATE, bounds, max_workers=2)

        # 2x2 grid => 4 tiles
        assert len(results) == 4
        for coord, data in results.items():
            assert data == b"IMG"
            assert coord[2] == 2  # zoom

    def test_skips_failed_tiles(self):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("500")

        with patch("tilestitch.tile_fetcher._build_session") as mock_build:
            mock_session = MagicMock()
            mock_session.get.return_value = mock_response
            mock_build.return_value = mock_session

            bounds = self._make_bounds()
            results = fetch_tiles(OSM_TEMPLATE, bounds, max_workers=2)

        assert len(results) == 0
