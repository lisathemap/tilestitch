from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_posterize import (
    PosterizeConfig,
    PosterizeError,
    apply_posterize,
    posterize_config_from_env,
)


def _solid(mode: str = "RGB", colour: tuple = (120, 80, 200)) -> Image.Image:
    img = Image.new(mode, (64, 64), colour if mode == "RGB" else colour + (255,))
    return img


class TestPosterizeConfig:
    def test_defaults(self):
        cfg = PosterizeConfig()
        assert cfg.enabled is True
        assert cfg.bits == 4

    def test_bits_stored(self):
        cfg = PosterizeConfig(bits=2)
        assert cfg.bits == 2

    def test_bits_one_valid(self):
        cfg = PosterizeConfig(bits=1)
        assert cfg.bits == 1

    def test_bits_eight_valid(self):
        cfg = PosterizeConfig(bits=8)
        assert cfg.bits == 8

    def test_zero_bits_raises(self):
        with pytest.raises(PosterizeError):
            PosterizeConfig(bits=0)

    def test_nine_bits_raises(self):
        with pytest.raises(PosterizeError):
            PosterizeConfig(bits=9)

    def test_negative_bits_raises(self):
        with pytest.raises(PosterizeError):
            PosterizeConfig(bits=-1)

    def test_invalid_enabled_raises(self):
        with pytest.raises(PosterizeError):
            PosterizeConfig(enabled="yes")  # type: ignore[arg-type]


class TestApplyPosterize:
    def test_returns_image(self):
        img = _solid()
        result = apply_posterize(img, PosterizeConfig())
        assert isinstance(result, Image.Image)

    def test_size_preserved(self):
        img = _solid()
        result = apply_posterize(img, PosterizeConfig())
        assert result.size == img.size

    def test_disabled_returns_original(self):
        img = _solid()
        result = apply_posterize(img, PosterizeConfig(enabled=False))
        assert result is img

    def test_rgba_alpha_preserved(self):
        img = _solid(mode="RGBA", colour=(100, 150, 200))
        result = apply_posterize(img, PosterizeConfig(bits=2))
        assert result.mode == "RGBA"
        assert result.size == img.size

    def test_low_bits_reduces_colours(self):
        img = Image.new("RGB", (16, 16))
        pixels = [(i * 4, i * 2, 255 - i * 3) for i in range(16)] * 16
        img.putdata(pixels)
        result = apply_posterize(img, PosterizeConfig(bits=1))
        unique = set(result.getdata())
        assert len(unique) <= 8  # 2^1 per channel => max 8 combos


class TestPosterizeConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_POSTERIZE_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_POSTERIZE_BITS", raising=False)
        cfg = posterize_config_from_env()
        assert cfg.enabled is True
        assert cfg.bits == 4

    def test_disabled_via_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_POSTERIZE_ENABLED", "false")
        cfg = posterize_config_from_env()
        assert cfg.enabled is False

    def test_bits_via_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_POSTERIZE_BITS", "3")
        cfg = posterize_config_from_env()
        assert cfg.bits == 3

    def test_invalid_bits_env_raises(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_POSTERIZE_BITS", "abc")
        with pytest.raises(PosterizeError):
            posterize_config_from_env()
