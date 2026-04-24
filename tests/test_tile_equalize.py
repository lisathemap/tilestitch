"""Tests for tilestitch.tile_equalize."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_equalize import (
    EqualizeConfig,
    EqualizeError,
    apply_equalize,
    equalize_config_from_env,
)


def _solid(mode: str = "RGB", colour=(128, 64, 32)) -> Image.Image:
    img = Image.new(mode, (64, 64))
    if mode == "RGBA":
        img.paste((colour[0], colour[1], colour[2], 200), (0, 0, 64, 64))
    elif mode == "L":
        img.paste(colour[0], (0, 0, 64, 64))
    else:
        img.paste(colour, (0, 0, 64, 64))
    return img


class TestEqualizeConfig:
    def test_defaults(self):
        cfg = EqualizeConfig()
        assert cfg.enabled is True
        assert cfg.mode == "full"
        assert cfg.mask is False

    def test_mode_normalised_to_lowercase(self):
        cfg = EqualizeConfig(mode="FULL")
        assert cfg.mode == "full"

    def test_whitespace_stripped_from_mode(self):
        cfg = EqualizeConfig(mode="  clahe  ")
        assert cfg.mode == "clahe"

    def test_clahe_mode_valid(self):
        cfg = EqualizeConfig(mode="clahe")
        assert cfg.mode == "clahe"

    def test_invalid_mode_raises(self):
        with pytest.raises(EqualizeError, match="Unknown equalization mode"):
            EqualizeConfig(mode="unknown")

    def test_empty_mode_raises(self):
        with pytest.raises(EqualizeError):
            EqualizeConfig(mode="")

    def test_mask_stored(self):
        cfg = EqualizeConfig(mask=True)
        assert cfg.mask is True


class TestApplyEqualize:
    def test_returns_image(self):
        img = _solid()
        result = apply_equalize(img, EqualizeConfig())
        assert isinstance(result, Image.Image)

    def test_disabled_returns_same_object(self):
        img = _solid()
        cfg = EqualizeConfig(enabled=False)
        result = apply_equalize(img, cfg)
        assert result is img

    def test_full_mode_rgb(self):
        img = _solid("RGB")
        result = apply_equalize(img, EqualizeConfig(mode="full"))
        assert result.mode == "RGB"
        assert result.size == img.size

    def test_full_mode_rgba_preserves_alpha(self):
        img = _solid("RGBA")
        result = apply_equalize(img, EqualizeConfig(mode="full"))
        assert result.mode == "RGBA"
        _, _, _, a_orig = img.split()
        _, _, _, a_result = result.split()
        assert list(a_orig.getdata()) == list(a_result.getdata())

    def test_full_mode_grayscale(self):
        img = _solid("L", colour=(100,))
        result = apply_equalize(img, EqualizeConfig(mode="full"))
        assert result.mode == "L"

    def test_clahe_mode_rgb(self):
        img = _solid("RGB")
        result = apply_equalize(img, EqualizeConfig(mode="clahe"))
        assert result.mode == "RGB"
        assert result.size == img.size

    def test_clahe_mode_rgba_preserves_alpha(self):
        img = _solid("RGBA")
        result = apply_equalize(img, EqualizeConfig(mode="clahe"))
        assert result.mode == "RGBA"


class TestEqualizeConfigFromEnv:
    def test_defaults_without_env(self, monkeypatch):
        for key in (
            "TILESTITCH_EQUALIZE_ENABLED",
            "TILESTITCH_EQUALIZE_MODE",
            "TILESTITCH_EQUALIZE_MASK",
        ):
            monkeypatch.delenv(key, raising=False)
        cfg = equalize_config_from_env()
        assert cfg.enabled is True
        assert cfg.mode == "full"
        assert cfg.mask is False

    def test_env_disables(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_EQUALIZE_ENABLED", "false")
        cfg = equalize_config_from_env()
        assert cfg.enabled is False

    def test_env_sets_mode(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_EQUALIZE_MODE", "clahe")
        cfg = equalize_config_from_env()
        assert cfg.mode == "clahe"

    def test_env_enables_mask(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_EQUALIZE_MASK", "true")
        cfg = equalize_config_from_env()
        assert cfg.mask is True
