"""Tests for tilestitch.tile_edge."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_edge import EdgeConfig, EdgeError, apply_edge, edge_config_from_env


def _solid(mode: str = "RGB", colour=(120, 80, 40)) -> Image.Image:
    img = Image.new(mode, (64, 64), colour)
    return img


class TestEdgeConfig:
    def test_defaults(self) -> None:
        cfg = EdgeConfig()
        assert cfg.enabled is False
        assert cfg.mode == "find"

    def test_find_mode_valid(self) -> None:
        cfg = EdgeConfig(mode="find")
        assert cfg.mode == "find"

    def test_enhance_mode_valid(self) -> None:
        cfg = EdgeConfig(mode="enhance")
        assert cfg.mode == "enhance"

    def test_invalid_mode_raises(self) -> None:
        with pytest.raises(EdgeError):
            EdgeConfig(mode="blur")

    def test_empty_mode_raises(self) -> None:
        with pytest.raises(EdgeError):
            EdgeConfig(mode="")


class TestApplyEdge:
    def test_disabled_returns_same_object(self) -> None:
        img = _solid()
        cfg = EdgeConfig(enabled=False)
        result = apply_edge(img, cfg)
        assert result is img

    def test_find_returns_image(self) -> None:
        img = _solid()
        cfg = EdgeConfig(enabled=True, mode="find")
        result = apply_edge(img, cfg)
        assert isinstance(result, Image.Image)

    def test_enhance_returns_image(self) -> None:
        img = _solid()
        cfg = EdgeConfig(enabled=True, mode="enhance")
        result = apply_edge(img, cfg)
        assert isinstance(result, Image.Image)

    def test_output_size_preserved(self) -> None:
        img = _solid()
        cfg = EdgeConfig(enabled=True, mode="find")
        result = apply_edge(img, cfg)
        assert result.size == img.size

    def test_rgb_mode_preserved(self) -> None:
        img = _solid(mode="RGB")
        cfg = EdgeConfig(enabled=True, mode="find")
        result = apply_edge(img, cfg)
        assert result.mode == "RGB"

    def test_rgba_mode_preserved(self) -> None:
        img = _solid(mode="RGBA", colour=(120, 80, 40, 200))
        cfg = EdgeConfig(enabled=True, mode="find")
        result = apply_edge(img, cfg)
        assert result.mode == "RGBA"


class TestEdgeConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch) -> None:
        monkeypatch.delenv("TILESTITCH_EDGE_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_EDGE_MODE", raising=False)
        cfg = edge_config_from_env()
        assert cfg.enabled is False
        assert cfg.mode == "find"

    def test_enabled_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("TILESTITCH_EDGE_ENABLED", "true")
        cfg = edge_config_from_env()
        assert cfg.enabled is True

    def test_mode_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("TILESTITCH_EDGE_MODE", "enhance")
        cfg = edge_config_from_env()
        assert cfg.mode == "enhance"
