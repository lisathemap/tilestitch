"""Tests for tilestitch.tile_histogram and tilestitch.histogram_pipeline."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_histogram import (
    HistogramConfig,
    HistogramError,
    apply_histogram,
    histogram_config_from_env,
)
from tilestitch.histogram_pipeline import HistogramStage, build_histogram_stage


def _solid(colour: tuple[int, int, int] = (80, 120, 200), size: int = 16) -> Image.Image:
    img = Image.new("RGB", (size, size), colour)
    return img


# ---------------------------------------------------------------------------
# HistogramConfig
# ---------------------------------------------------------------------------

class TestHistogramConfig:
    def test_defaults(self):
        cfg = HistogramConfig()
        assert cfg.enabled is False
        assert cfg.mode == "equalize"

    def test_mode_normalised(self):
        cfg = HistogramConfig(mode="  Equalize  ")
        assert cfg.mode == "equalize"

    def test_stretch_mode_valid(self):
        cfg = HistogramConfig(mode="stretch")
        assert cfg.mode == "stretch"

    def test_invalid_mode_raises(self):
        with pytest.raises(HistogramError):
            HistogramConfig(mode="histogram_magic")

    def test_whitespace_only_mode_raises(self):
        with pytest.raises(HistogramError):
            HistogramConfig(mode="   ")


# ---------------------------------------------------------------------------
# apply_histogram
# ---------------------------------------------------------------------------

class TestApplyHistogram:
    def test_disabled_returns_same_object(self):
        img = _solid()
        cfg = HistogramConfig(enabled=False)
        assert apply_histogram(img, cfg) is img

    def test_equalize_returns_image(self):
        img = _solid()
        cfg = HistogramConfig(enabled=True, mode="equalize")
        result = apply_histogram(img, cfg)
        assert isinstance(result, Image.Image)
        assert result.size == img.size

    def test_stretch_returns_image(self):
        img = _solid()
        cfg = HistogramConfig(enabled=True, mode="stretch")
        result = apply_histogram(img, cfg)
        assert isinstance(result, Image.Image)
        assert result.size == img.size

    def test_rgba_input_preserved(self):
        img = Image.new("RGBA", (16, 16), (100, 150, 200, 128))
        cfg = HistogramConfig(enabled=True, mode="equalize")
        result = apply_histogram(img, cfg)
        assert result.mode == "RGBA"

    def test_grayscale_input_preserved(self):
        img = Image.new("L", (16, 16), 128)
        cfg = HistogramConfig(enabled=True, mode="equalize")
        result = apply_histogram(img, cfg)
        assert result.mode == "L"


# ---------------------------------------------------------------------------
# histogram_config_from_env
# ---------------------------------------------------------------------------

def test_env_defaults(monkeypatch):
    monkeypatch.delenv("TILESTITCH_HISTOGRAM_ENABLED", raising=False)
    monkeypatch.delenv("TILESTITCH_HISTOGRAM_MODE", raising=False)
    cfg = histogram_config_from_env()
    assert cfg.enabled is False
    assert cfg.mode == "equalize"


def test_env_enabled(monkeypatch):
    monkeypatch.setenv("TILESTITCH_HISTOGRAM_ENABLED", "true")
    monkeypatch.setenv("TILESTITCH_HISTOGRAM_MODE", "stretch")
    cfg = histogram_config_from_env()
    assert cfg.enabled is True
    assert cfg.mode == "stretch"


# ---------------------------------------------------------------------------
# HistogramStage / build_histogram_stage
# ---------------------------------------------------------------------------

class TestHistogramStage:
    def test_returns_same_image_when_config_none(self):
        stage = HistogramStage(config=None)
        img = _solid()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        stage = HistogramStage(config=HistogramConfig(enabled=False))
        img = _solid()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        stage = HistogramStage(config=HistogramConfig(enabled=True))
        img = _solid()
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_build_returns_stage(self):
        stage = build_histogram_stage(HistogramConfig(enabled=False))
        assert isinstance(stage, HistogramStage)
