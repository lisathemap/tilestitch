"""Tests for tilestitch.tile_noise."""
import pytest
from PIL import Image

from tilestitch.tile_noise import (
    NoiseConfig,
    NoiseError,
    apply_noise_reduction,
    noise_config_from_env,
)


def _solid(mode: str = "RGB", size: int = 64, colour=None) -> Image.Image:
    if colour is None:
        colour = (120, 130, 140) if mode == "RGB" else 128
    return Image.new(mode, (size, size), colour)


class TestNoiseConfig:
    def test_defaults(self):
        cfg = NoiseConfig()
        assert cfg.enabled is False
        assert cfg.radius == 1

    def test_radius_stored(self):
        cfg = NoiseConfig(radius=3)
        assert cfg.radius == 3

    def test_zero_radius_raises(self):
        with pytest.raises(NoiseError):
            NoiseConfig(radius=0)

    def test_negative_radius_raises(self):
        with pytest.raises(NoiseError):
            NoiseConfig(radius=-1)

    def test_radius_above_ten_raises(self):
        with pytest.raises(NoiseError):
            NoiseConfig(radius=11)

    def test_radius_ten_valid(self):
        cfg = NoiseConfig(radius=10)
        assert cfg.radius == 10


class TestApplyNoiseReduction:
    def test_returns_image_when_disabled(self):
        img = _solid()
        cfg = NoiseConfig(enabled=False)
        result = apply_noise_reduction(img, cfg)
        assert result is img

    def test_returns_image_instance_when_enabled(self):
        img = _solid()
        cfg = NoiseConfig(enabled=True, radius=1)
        result = apply_noise_reduction(img, cfg)
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self):
        img = _solid(size=64)
        cfg = NoiseConfig(enabled=True, radius=2)
        result = apply_noise_reduction(img, cfg)
        assert result.size == img.size

    def test_rgba_mode_preserved(self):
        img = _solid(mode="RGBA", colour=(100, 100, 100, 255))
        cfg = NoiseConfig(enabled=True)
        result = apply_noise_reduction(img, cfg)
        assert result.mode == "RGBA"

    def test_grayscale_mode_preserved(self):
        img = _solid(mode="L", colour=128)
        cfg = NoiseConfig(enabled=True)
        result = apply_noise_reduction(img, cfg)
        assert result.mode == "L"


class TestNoiseConfigFromEnv:
    def test_defaults_when_env_unset(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_NOISE_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_NOISE_RADIUS", raising=False)
        cfg = noise_config_from_env()
        assert cfg.enabled is False
        assert cfg.radius == 1

    def test_enabled_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_NOISE_ENABLED", "true")
        cfg = noise_config_from_env()
        assert cfg.enabled is True

    def test_radius_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_NOISE_RADIUS", "3")
        cfg = noise_config_from_env()
        assert cfg.radius == 3
