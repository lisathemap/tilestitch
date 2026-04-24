"""Tests for tilestitch.tile_kuwahara."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_kuwahara import (
    KuwaharaConfig,
    KuwaharaError,
    apply_kuwahara,
    kuwahara_config_from_env,
)


def _solid(colour: tuple, size: int = 32, mode: str = "RGB") -> Image.Image:
    img = Image.new(mode, (size, size), colour)
    return img


# ---------------------------------------------------------------------------
# KuwaharaConfig
# ---------------------------------------------------------------------------

class TestKuwaharaConfig:
    def test_defaults(self):
        cfg = KuwaharaConfig()
        assert cfg.enabled is True
        assert cfg.radius == 3

    def test_radius_stored(self):
        cfg = KuwaharaConfig(radius=5)
        assert cfg.radius == 5

    def test_zero_radius_raises(self):
        with pytest.raises(KuwaharaError):
            KuwaharaConfig(radius=0)

    def test_negative_radius_raises(self):
        with pytest.raises(KuwaharaError):
            KuwaharaConfig(radius=-1)

    def test_radius_above_max_raises(self):
        with pytest.raises(KuwaharaError):
            KuwaharaConfig(radius=11)

    def test_radius_at_max_valid(self):
        cfg = KuwaharaConfig(radius=10)
        assert cfg.radius == 10

    def test_radius_one_valid(self):
        cfg = KuwaharaConfig(radius=1)
        assert cfg.radius == 1

    def test_disabled_flag(self):
        cfg = KuwaharaConfig(enabled=False)
        assert cfg.enabled is False


# ---------------------------------------------------------------------------
# kuwahara_config_from_env
# ---------------------------------------------------------------------------

def test_env_defaults(monkeypatch):
    monkeypatch.delenv("TILESTITCH_KUWAHARA_ENABLED", raising=False)
    monkeypatch.delenv("TILESTITCH_KUWAHARA_RADIUS", raising=False)
    cfg = kuwahara_config_from_env()
    assert cfg.enabled is True
    assert cfg.radius == 3


def test_env_disabled(monkeypatch):
    monkeypatch.setenv("TILESTITCH_KUWAHARA_ENABLED", "false")
    cfg = kuwahara_config_from_env()
    assert cfg.enabled is False


def test_env_radius(monkeypatch):
    monkeypatch.setenv("TILESTITCH_KUWAHARA_RADIUS", "2")
    cfg = kuwahara_config_from_env()
    assert cfg.radius == 2


# ---------------------------------------------------------------------------
# apply_kuwahara
# ---------------------------------------------------------------------------

def test_returns_image():
    img = _solid((100, 150, 200))
    result = apply_kuwahara(img, KuwaharaConfig(radius=1))
    assert isinstance(result, Image.Image)


def test_output_size_preserved():
    img = _solid((80, 80, 80), size=16)
    result = apply_kuwahara(img, KuwaharaConfig(radius=1))
    assert result.size == img.size


def test_disabled_returns_original():
    img = _solid((10, 20, 30))
    result = apply_kuwahara(img, KuwaharaConfig(enabled=False))
    assert result is img


def test_rgba_alpha_preserved():
    img = _solid((255, 0, 0, 128), size=16, mode="RGBA")
    result = apply_kuwahara(img, KuwaharaConfig(radius=1))
    assert result.mode == "RGBA"
    # Alpha channel should be unchanged
    assert result.split()[3].getpixel((8, 8)) == 128


def test_uniform_image_unchanged():
    """A uniform-colour image should be unchanged after Kuwahara."""
    colour = (123, 45, 67)
    img = _solid(colour, size=16)
    result = apply_kuwahara(img, KuwaharaConfig(radius=2))
    px = result.getpixel((8, 8))
    assert px == colour
