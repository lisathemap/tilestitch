"""Tests for tilestitch.tile_scanlines."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_scanlines import (
    ScanlinesConfig,
    ScanlinesError,
    apply_scanlines,
    scanlines_config_from_env,
)


def _solid(colour: tuple[int, int, int] = (200, 200, 200), size: int = 64) -> Image.Image:
    return Image.new("RGB", (size, size), colour)


class TestScanlinesConfig:
    def test_defaults(self) -> None:
        cfg = ScanlinesConfig()
        assert cfg.enabled is True
        assert cfg.line_spacing == 4
        assert cfg.opacity == 0.3
        assert cfg.colour == "#000000"

    def test_spacing_stored(self) -> None:
        cfg = ScanlinesConfig(line_spacing=8)
        assert cfg.line_spacing == 8

    def test_zero_spacing_raises(self) -> None:
        with pytest.raises(ScanlinesError, match="line_spacing"):
            ScanlinesConfig(line_spacing=0)

    def test_negative_spacing_raises(self) -> None:
        with pytest.raises(ScanlinesError, match="line_spacing"):
            ScanlinesConfig(line_spacing=-1)

    def test_opacity_stored(self) -> None:
        cfg = ScanlinesConfig(opacity=0.5)
        assert cfg.opacity == 0.5

    def test_opacity_zero_valid(self) -> None:
        cfg = ScanlinesConfig(opacity=0.0)
        assert cfg.opacity == 0.0

    def test_opacity_one_valid(self) -> None:
        cfg = ScanlinesConfig(opacity=1.0)
        assert cfg.opacity == 1.0

    def test_opacity_above_one_raises(self) -> None:
        with pytest.raises(ScanlinesError, match="opacity"):
            ScanlinesConfig(opacity=1.1)

    def test_opacity_below_zero_raises(self) -> None:
        with pytest.raises(ScanlinesError, match="opacity"):
            ScanlinesConfig(opacity=-0.1)

    def test_empty_colour_raises(self) -> None:
        with pytest.raises(ScanlinesError, match="colour"):
            ScanlinesConfig(colour="")

    def test_whitespace_colour_raises(self) -> None:
        with pytest.raises(ScanlinesError, match="colour"):
            ScanlinesConfig(colour="   ")


class TestApplyScanlines:
    def test_returns_image(self) -> None:
        img = _solid()
        result = apply_scanlines(img, ScanlinesConfig())
        assert isinstance(result, Image.Image)

    def test_output_same_size(self) -> None:
        img = _solid(size=64)
        result = apply_scanlines(img, ScanlinesConfig())
        assert result.size == img.size

    def test_disabled_returns_original(self) -> None:
        img = _solid()
        result = apply_scanlines(img, ScanlinesConfig(enabled=False))
        assert result is img

    def test_output_mode_preserved_rgb(self) -> None:
        img = _solid()
        result = apply_scanlines(img, ScanlinesConfig())
        assert result.mode == "RGB"

    def test_output_mode_preserved_rgba(self) -> None:
        img = Image.new("RGBA", (32, 32), (100, 100, 100, 255))
        result = apply_scanlines(img, ScanlinesConfig())
        assert result.mode == "RGBA"

    def test_invalid_colour_raises(self) -> None:
        img = _solid()
        with pytest.raises(ScanlinesError, match="invalid colour"):
            apply_scanlines(img, ScanlinesConfig.__new__(ScanlinesConfig).__class__(
                colour="not-a-colour"
            ))


class TestScanlinesConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for key in (
            "TILESTITCH_SCANLINES_ENABLED",
            "TILESTITCH_SCANLINES_SPACING",
            "TILESTITCH_SCANLINES_OPACITY",
            "TILESTITCH_SCANLINES_COLOUR",
        ):
            monkeypatch.delenv(key, raising=False)
        cfg = scanlines_config_from_env()
        assert cfg == ScanlinesConfig()

    def test_reads_spacing_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_SCANLINES_SPACING", "10")
        cfg = scanlines_config_from_env()
        assert cfg.line_spacing == 10

    def test_reads_opacity_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_SCANLINES_OPACITY", "0.6")
        cfg = scanlines_config_from_env()
        assert cfg.opacity == pytest.approx(0.6)

    def test_reads_enabled_false_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_SCANLINES_ENABLED", "false")
        cfg = scanlines_config_from_env()
        assert cfg.enabled is False

    def test_reads_colour_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_SCANLINES_COLOUR", "#ffffff")
        cfg = scanlines_config_from_env()
        assert cfg.colour == "#ffffff"
