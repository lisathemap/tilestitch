"""Tests for tilestitch.tile_grayscale."""
import os
import pytest
from PIL import Image

from tilestitch.tile_grayscale import (
    GrayscaleConfig,
    GrayscaleError,
    GrayscaleStage,
    build_grayscale_stage,
    convert_to_grayscale,
    grayscale_config_from_env,
)


def _rgb(colour=(100, 150, 200)) -> Image.Image:
    img = Image.new("RGB", (4, 4), colour)
    return img


def _rgba(colour=(100, 150, 200, 128)) -> Image.Image:
    img = Image.new("RGBA", (4, 4), colour)
    return img


# --- GrayscaleConfig ---

class TestGrayscaleConfig:
    def test_defaults(self):
        cfg = GrayscaleConfig()
        assert cfg.enabled is False
        assert cfg.keep_alpha is True

    def test_invalid_enabled_raises(self):
        with pytest.raises(GrayscaleError):
            GrayscaleConfig(enabled="yes")  # type: ignore

    def test_invalid_keep_alpha_raises(self):
        with pytest.raises(GrayscaleError):
            GrayscaleConfig(keep_alpha=1)  # type: ignore


# --- convert_to_grayscale ---

class TestConvertToGrayscale:
    def test_disabled_returns_same_object(self):
        cfg = GrayscaleConfig(enabled=False)
        img = _rgb()
        assert convert_to_grayscale(img, cfg) is img

    def test_rgb_converted_to_l(self):
        cfg = GrayscaleConfig(enabled=True)
        result = convert_to_grayscale(_rgb(), cfg)
        assert result.mode == "L"

    def test_rgba_keep_alpha_returns_la(self):
        cfg = GrayscaleConfig(enabled=True, keep_alpha=True)
        result = convert_to_grayscale(_rgba(), cfg)
        assert result.mode == "LA"

    def test_rgba_no_keep_alpha_returns_l(self):
        cfg = GrayscaleConfig(enabled=True, keep_alpha=False)
        result = convert_to_grayscale(_rgba(), cfg)
        assert result.mode == "L"

    def test_unsupported_mode_raises(self):
        cfg = GrayscaleConfig(enabled=True)
        img = Image.new("CMYK", (4, 4))
        with pytest.raises(GrayscaleError):
            convert_to_grayscale(img, cfg)

    def test_size_preserved(self):
        cfg = GrayscaleConfig(enabled=True)
        img = Image.new("RGB", (16, 32))
        result = convert_to_grayscale(img, cfg)
        assert result.size == (16, 32)


# --- GrayscaleStage ---

class TestGrayscaleStage:
    def test_returns_image_when_enabled(self):
        cfg = GrayscaleConfig(enabled=True)
        stage = GrayscaleStage(config=cfg)
        result = stage.process(_rgb())
        assert result.mode == "L"

    def test_returns_same_image_when_disabled(self):
        cfg = GrayscaleConfig(enabled=False)
        stage = GrayscaleStage(config=cfg)
        img = _rgb()
        assert stage.process(img) is img

    def test_returns_same_image_when_config_none(self):
        stage = GrayscaleStage(config=None)
        img = _rgb()
        assert stage.process(img) is img


# --- grayscale_config_from_env ---

def test_env_enabled(monkeypatch):
    monkeypatch.setenv("TILESTITCH_GRAYSCALE", "true")
    cfg = grayscale_config_from_env()
    assert cfg.enabled is True


def test_env_keep_alpha_false(monkeypatch):
    monkeypatch.setenv("TILESTITCH_GRAYSCALE_KEEP_ALPHA", "false")
    cfg = grayscale_config_from_env()
    assert cfg.keep_alpha is False


def test_build_grayscale_stage_returns_stage():
    stage = build_grayscale_stage(GrayscaleConfig(enabled=False))
    assert isinstance(stage, GrayscaleStage)
