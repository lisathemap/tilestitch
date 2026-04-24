"""Tests for tilestitch.tile_spotlight."""

import pytest
from PIL import Image

from tilestitch.tile_spotlight import (
    SpotlightConfig,
    SpotlightError,
    apply_spotlight,
    spotlight_config_from_env,
)


def _solid(colour: tuple = (120, 80, 40), size: int = 64) -> Image.Image:
    img = Image.new("RGB", (size, size), colour)
    return img


class TestSpotlightConfig:
    def test_defaults(self):
        cfg = SpotlightConfig()
        assert cfg.cx == 0.5
        assert cfg.cy == 0.5
        assert cfg.radius == 0.4
        assert cfg.strength == 0.7
        assert cfg.enabled is True

    def test_cx_below_zero_raises(self):
        with pytest.raises(SpotlightError):
            SpotlightConfig(cx=-0.1)

    def test_cx_above_one_raises(self):
        with pytest.raises(SpotlightError):
            SpotlightConfig(cx=1.1)

    def test_cy_below_zero_raises(self):
        with pytest.raises(SpotlightError):
            SpotlightConfig(cy=-0.1)

    def test_cy_above_one_raises(self):
        with pytest.raises(SpotlightError):
            SpotlightConfig(cy=1.1)

    def test_radius_zero_valid(self):
        cfg = SpotlightConfig(radius=0.0)
        assert cfg.radius == 0.0

    def test_radius_one_valid(self):
        cfg = SpotlightConfig(radius=1.0)
        assert cfg.radius == 1.0

    def test_radius_above_one_raises(self):
        with pytest.raises(SpotlightError):
            SpotlightConfig(radius=1.1)

    def test_strength_zero_valid(self):
        cfg = SpotlightConfig(strength=0.0)
        assert cfg.strength == 0.0

    def test_strength_above_one_raises(self):
        with pytest.raises(SpotlightError):
            SpotlightConfig(strength=1.5)

    def test_strength_negative_raises(self):
        with pytest.raises(SpotlightError):
            SpotlightConfig(strength=-0.1)


class TestApplySpotlight:
    def test_returns_image(self):
        img = _solid()
        result = apply_spotlight(img, SpotlightConfig())
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self):
        img = _solid(size=64)
        result = apply_spotlight(img, SpotlightConfig())
        assert result.size == (64, 64)

    def test_output_mode_matches_input_rgb(self):
        img = _solid()
        result = apply_spotlight(img, SpotlightConfig())
        assert result.mode == "RGB"

    def test_output_mode_matches_input_rgba(self):
        img = _solid().convert("RGBA")
        result = apply_spotlight(img, SpotlightConfig())
        assert result.mode == "RGBA"

    def test_corner_pixel_dimmer_than_centre(self):
        img = Image.new("RGB", (64, 64), (200, 200, 200))
        cfg = SpotlightConfig(cx=0.5, cy=0.5, radius=0.3, strength=0.2)
        result = apply_spotlight(img, cfg)
        centre = result.getpixel((32, 32))
        corner = result.getpixel((0, 0))
        assert sum(corner) < sum(centre)

    def test_env_defaults_produce_config(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_SPOTLIGHT_CX", raising=False)
        cfg = spotlight_config_from_env()
        assert cfg.cx == 0.5

    def test_env_override_cx(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SPOTLIGHT_CX", "0.3")
        cfg = spotlight_config_from_env()
        assert cfg.cx == pytest.approx(0.3)

    def test_env_override_enabled_false(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SPOTLIGHT_ENABLED", "false")
        cfg = spotlight_config_from_env()
        assert cfg.enabled is False
