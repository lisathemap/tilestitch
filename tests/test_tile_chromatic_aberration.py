"""Tests for tile_chromatic_aberration and chromatic_aberration_pipeline."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_chromatic_aberration import (
    ChromaticAberrationConfig,
    ChromaticAberrationError,
    apply_chromatic_aberration,
    chromatic_aberration_config_from_env,
)
from tilestitch.chromatic_aberration_pipeline import (
    ChromaticAberrationStage,
    build_chromatic_aberration_stage,
)


def _solid(colour: tuple[int, int, int] = (120, 80, 200)) -> Image.Image:
    img = Image.new("RGB", (64, 64), colour)
    return img


# ---------------------------------------------------------------------------
# ChromaticAberrationConfig
# ---------------------------------------------------------------------------

class TestChromaticAberrationConfig:
    def test_defaults(self):
        cfg = ChromaticAberrationConfig()
        assert cfg.shift == 3
        assert cfg.enabled is True

    def test_shift_stored(self):
        cfg = ChromaticAberrationConfig(shift=10)
        assert cfg.shift == 10

    def test_zero_shift_valid(self):
        cfg = ChromaticAberrationConfig(shift=0)
        assert cfg.shift == 0

    def test_negative_shift_raises(self):
        with pytest.raises(ChromaticAberrationError):
            ChromaticAberrationConfig(shift=-1)

    def test_shift_above_max_raises(self):
        with pytest.raises(ChromaticAberrationError):
            ChromaticAberrationConfig(shift=51)

    def test_max_shift_valid(self):
        cfg = ChromaticAberrationConfig(shift=50)
        assert cfg.shift == 50

    def test_disabled_stored(self):
        cfg = ChromaticAberrationConfig(enabled=False)
        assert cfg.enabled is False


# ---------------------------------------------------------------------------
# apply_chromatic_aberration
# ---------------------------------------------------------------------------

class TestApplyChromaticAberration:
    def test_returns_image(self):
        img = _solid()
        result = apply_chromatic_aberration(img, ChromaticAberrationConfig())
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self):
        img = _solid()
        result = apply_chromatic_aberration(img, ChromaticAberrationConfig(shift=5))
        assert result.size == img.size

    def test_zero_shift_returns_equivalent(self):
        img = _solid()
        result = apply_chromatic_aberration(img, ChromaticAberrationConfig(shift=0))
        assert result.size == img.size

    def test_disabled_returns_same_object(self):
        img = _solid()
        cfg = ChromaticAberrationConfig(enabled=False)
        result = apply_chromatic_aberration(img, cfg)
        assert result is img

    def test_rgba_input_preserved(self):
        img = Image.new("RGBA", (64, 64), (100, 150, 200, 255))
        result = apply_chromatic_aberration(img, ChromaticAberrationConfig(shift=4))
        assert result.mode == "RGBA"


# ---------------------------------------------------------------------------
# chromatic_aberration_config_from_env
# ---------------------------------------------------------------------------

class TestChromaticAberrationConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_CA_SHIFT", raising=False)
        monkeypatch.delenv("TILESTITCH_CA_ENABLED", raising=False)
        cfg = chromatic_aberration_config_from_env()
        assert cfg.shift == 3
        assert cfg.enabled is True

    def test_reads_shift_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_CA_SHIFT", "7")
        cfg = chromatic_aberration_config_from_env()
        assert cfg.shift == 7

    def test_disabled_via_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_CA_ENABLED", "false")
        cfg = chromatic_aberration_config_from_env()
        assert cfg.enabled is False

    def test_invalid_shift_raises(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_CA_SHIFT", "notanint")
        with pytest.raises(ChromaticAberrationError):
            chromatic_aberration_config_from_env()


# ---------------------------------------------------------------------------
# ChromaticAberrationStage
# ---------------------------------------------------------------------------

class TestChromaticAberrationStage:
    def test_returns_same_image_when_config_none(self):
        stage = ChromaticAberrationStage(config=None)
        img = _solid()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        cfg = ChromaticAberrationConfig(enabled=False)
        stage = ChromaticAberrationStage(config=cfg)
        img = _solid()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        cfg = ChromaticAberrationConfig(shift=3)
        stage = ChromaticAberrationStage(config=cfg)
        img = _solid()
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_build_stage_has_default_config(self):
        stage = build_chromatic_aberration_stage()
        assert stage.config is not None
        assert stage.config.shift == 3
