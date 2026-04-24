"""Tests for tilestitch.tile_glitch."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_glitch import (
    GlitchConfig,
    GlitchError,
    apply_glitch,
    glitch_config_from_env,
)


def _solid(colour: tuple[int, int, int] = (100, 150, 200), size: int = 64) -> Image.Image:
    return Image.new("RGB", (size, size), colour)


class TestGlitchConfig:
    def test_defaults(self) -> None:
        cfg = GlitchConfig()
        assert cfg.enabled is True
        assert cfg.intensity == pytest.approx(0.3)
        assert cfg.max_shift == 20
        assert cfg.seed is None

    def test_intensity_zero_valid(self) -> None:
        cfg = GlitchConfig(intensity=0.0)
        assert cfg.intensity == 0.0

    def test_intensity_one_valid(self) -> None:
        cfg = GlitchConfig(intensity=1.0)
        assert cfg.intensity == 1.0

    def test_intensity_above_one_raises(self) -> None:
        with pytest.raises(GlitchError, match="intensity"):
            GlitchConfig(intensity=1.1)

    def test_intensity_below_zero_raises(self) -> None:
        with pytest.raises(GlitchError, match="intensity"):
            GlitchConfig(intensity=-0.1)

    def test_max_shift_zero_raises(self) -> None:
        with pytest.raises(GlitchError, match="max_shift"):
            GlitchConfig(max_shift=0)

    def test_max_shift_negative_raises(self) -> None:
        with pytest.raises(GlitchError, match="max_shift"):
            GlitchConfig(max_shift=-5)

    def test_seed_stored(self) -> None:
        cfg = GlitchConfig(seed=42)
        assert cfg.seed == 42


class TestApplyGlitch:
    def test_returns_image(self) -> None:
        img = _solid()
        result = apply_glitch(img, GlitchConfig())
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self) -> None:
        img = _solid(size=64)
        result = apply_glitch(img, GlitchConfig(seed=0))
        assert result.size == img.size

    def test_disabled_returns_original(self) -> None:
        img = _solid()
        result = apply_glitch(img, GlitchConfig(enabled=False))
        assert result is img

    def test_seeded_run_is_deterministic(self) -> None:
        img = _solid(size=32)
        r1 = apply_glitch(img, GlitchConfig(seed=7, intensity=0.5))
        r2 = apply_glitch(img, GlitchConfig(seed=7, intensity=0.5))
        assert list(r1.getdata()) == list(r2.getdata())

    def test_different_seeds_differ(self) -> None:
        img = _solid(size=64)
        r1 = apply_glitch(img, GlitchConfig(seed=1, intensity=0.8, max_shift=10))
        r2 = apply_glitch(img, GlitchConfig(seed=99, intensity=0.8, max_shift=10))
        assert list(r1.getdata()) != list(r2.getdata())

    def test_output_mode_is_rgba(self) -> None:
        img = _solid()
        result = apply_glitch(img, GlitchConfig(seed=0))
        assert result.mode == "RGBA"


class TestGlitchConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for key in (
            "TILESTITCH_GLITCH_ENABLED",
            "TILESTITCH_GLITCH_INTENSITY",
            "TILESTITCH_GLITCH_MAX_SHIFT",
            "TILESTITCH_GLITCH_SEED",
        ):
            monkeypatch.delenv(key, raising=False)
        cfg = glitch_config_from_env()
        assert cfg.enabled is False
        assert cfg.intensity == pytest.approx(0.3)

    def test_enabled_via_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_GLITCH_ENABLED", "true")
        cfg = glitch_config_from_env()
        assert cfg.enabled is True

    def test_seed_via_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_GLITCH_SEED", "123")
        cfg = glitch_config_from_env()
        assert cfg.seed == 123

    def test_empty_seed_is_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_GLITCH_SEED", "")
        cfg = glitch_config_from_env()
        assert cfg.seed is None
