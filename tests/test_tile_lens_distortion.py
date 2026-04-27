"""Tests for tilestitch.tile_lens_distortion."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_lens_distortion import (
    LensDistortionConfig,
    LensDistortionError,
    apply_lens_distortion,
    lens_distortion_config_from_env,
)


def _solid(colour: tuple = (120, 80, 60, 255), size: tuple = (64, 64)) -> Image.Image:
    img = Image.new("RGBA", size, colour)
    return img


class TestLensDistortionConfig:
    def test_defaults(self):
        cfg = LensDistortionConfig()
        assert cfg.k1 == 0.1
        assert cfg.k2 == 0.0
        assert cfg.enabled is True

    def test_k1_stored(self):
        cfg = LensDistortionConfig(k1=0.5)
        assert cfg.k1 == 0.5

    def test_k2_stored(self):
        cfg = LensDistortionConfig(k2=-0.2)
        assert cfg.k2 == -0.2

    def test_k1_too_large_raises(self):
        with pytest.raises(LensDistortionError):
            LensDistortionConfig(k1=1.5)

    def test_k1_too_small_raises(self):
        with pytest.raises(LensDistortionError):
            LensDistortionConfig(k1=-1.5)

    def test_k2_too_large_raises(self):
        with pytest.raises(LensDistortionError):
            LensDistortionConfig(k2=2.0)

    def test_enabled_false_valid(self):
        cfg = LensDistortionConfig(enabled=False)
        assert cfg.enabled is False

    def test_invalid_enabled_raises(self):
        with pytest.raises(LensDistortionError):
            LensDistortionConfig(enabled="yes")  # type: ignore

    def test_k1_boundary_positive(self):
        cfg = LensDistortionConfig(k1=1.0)
        assert cfg.k1 == 1.0

    def test_k1_boundary_negative(self):
        cfg = LensDistortionConfig(k1=-1.0)
        assert cfg.k1 == -1.0


class TestApplyLensDistortion:
    def test_returns_image(self):
        img = _solid()
        cfg = LensDistortionConfig()
        result = apply_lens_distortion(img, cfg)
        assert isinstance(result, Image.Image)

    def test_output_size_preserved(self):
        img = _solid(size=(64, 64))
        cfg = LensDistortionConfig(k1=0.2)
        result = apply_lens_distortion(img, cfg)
        assert result.size == (64, 64)

    def test_disabled_returns_original(self):
        img = _solid()
        cfg = LensDistortionConfig(enabled=False)
        result = apply_lens_distortion(img, cfg)
        assert result is img

    def test_barrel_distortion_runs(self):
        img = _solid(size=(32, 32))
        cfg = LensDistortionConfig(k1=0.5, k2=0.0)
        result = apply_lens_distortion(img, cfg)
        assert result.size == (32, 32)

    def test_pincushion_distortion_runs(self):
        img = _solid(size=(32, 32))
        cfg = LensDistortionConfig(k1=-0.5)
        result = apply_lens_distortion(img, cfg)
        assert result.size == (32, 32)

    def test_output_mode_is_rgba(self):
        img = _solid()
        cfg = LensDistortionConfig()
        result = apply_lens_distortion(img, cfg)
        assert result.mode == "RGBA"


class TestLensDistortionConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_LENS_K1", raising=False)
        monkeypatch.delenv("TILESTITCH_LENS_K2", raising=False)
        monkeypatch.delenv("TILESTITCH_LENS_ENABLED", raising=False)
        cfg = lens_distortion_config_from_env()
        assert cfg.k1 == 0.1
        assert cfg.k2 == 0.0
        assert cfg.enabled is True

    def test_reads_k1_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_LENS_K1", "0.3")
        cfg = lens_distortion_config_from_env()
        assert cfg.k1 == pytest.approx(0.3)

    def test_reads_enabled_false_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_LENS_ENABLED", "false")
        cfg = lens_distortion_config_from_env()
        assert cfg.enabled is False
