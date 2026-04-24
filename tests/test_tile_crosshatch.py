from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_crosshatch import (
    CrosshatchConfig,
    CrosshatchError,
    apply_crosshatch,
    crosshatch_config_from_env,
)


def _solid(colour: tuple[int, int, int] = (200, 200, 200), size: int = 64) -> Image.Image:
    return Image.new("RGB", (size, size), colour)


class TestCrosshatchConfig:
    def test_defaults(self) -> None:
        cfg = CrosshatchConfig()
        assert cfg.enabled is True
        assert cfg.spacing == 16
        assert cfg.line_width == 1
        assert cfg.colour == "#000000"
        assert cfg.opacity == pytest.approx(0.3)

    def test_spacing_stored(self) -> None:
        cfg = CrosshatchConfig(spacing=8)
        assert cfg.spacing == 8

    def test_zero_spacing_raises(self) -> None:
        with pytest.raises(CrosshatchError, match="spacing"):
            CrosshatchConfig(spacing=0)

    def test_negative_spacing_raises(self) -> None:
        with pytest.raises(CrosshatchError, match="spacing"):
            CrosshatchConfig(spacing=-4)

    def test_one_spacing_raises(self) -> None:
        with pytest.raises(CrosshatchError, match="spacing"):
            CrosshatchConfig(spacing=1)

    def test_minimum_spacing_ok(self) -> None:
        cfg = CrosshatchConfig(spacing=2)
        assert cfg.spacing == 2

    def test_zero_line_width_raises(self) -> None:
        with pytest.raises(CrosshatchError, match="line_width"):
            CrosshatchConfig(line_width=0)

    def test_opacity_above_one_raises(self) -> None:
        with pytest.raises(CrosshatchError, match="opacity"):
            CrosshatchConfig(opacity=1.1)

    def test_opacity_below_zero_raises(self) -> None:
        with pytest.raises(CrosshatchError, match="opacity"):
            CrosshatchConfig(opacity=-0.1)

    def test_opacity_zero_valid(self) -> None:
        cfg = CrosshatchConfig(opacity=0.0)
        assert cfg.opacity == pytest.approx(0.0)

    def test_opacity_one_valid(self) -> None:
        cfg = CrosshatchConfig(opacity=1.0)
        assert cfg.opacity == pytest.approx(1.0)

    def test_invalid_colour_raises(self) -> None:
        with pytest.raises(CrosshatchError, match="colour"):
            CrosshatchConfig(colour="notacolour")

    def test_valid_colour_stored(self) -> None:
        cfg = CrosshatchConfig(colour="#ff0000")
        assert cfg.colour == "#ff0000"


class TestApplyCrosshatch:
    def test_returns_image(self) -> None:
        img = _solid()
        result = apply_crosshatch(img, CrosshatchConfig())
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self) -> None:
        img = _solid(size=64)
        result = apply_crosshatch(img, CrosshatchConfig())
        assert result.size == (64, 64)

    def test_disabled_returns_original(self) -> None:
        img = _solid()
        cfg = CrosshatchConfig(enabled=False)
        result = apply_crosshatch(img, cfg)
        assert result is img

    def test_output_mode_preserved_rgb(self) -> None:
        img = _solid()
        result = apply_crosshatch(img, CrosshatchConfig())
        assert result.mode == "RGB"

    def test_output_mode_preserved_rgba(self) -> None:
        img = Image.new("RGBA", (64, 64), (100, 100, 100, 255))
        result = apply_crosshatch(img, CrosshatchConfig())
        assert result.mode == "RGBA"


class TestCrosshatchConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for key in (
            "TILESTITCH_CROSSHATCH_ENABLED",
            "TILESTITCH_CROSSHATCH_SPACING",
            "TILESTITCH_CROSSHATCH_LINE_WIDTH",
            "TILESTITCH_CROSSHATCH_COLOUR",
            "TILESTITCH_CROSSHATCH_OPACITY",
        ):
            monkeypatch.delenv(key, raising=False)
        cfg = crosshatch_config_from_env()
        assert cfg.enabled is True
        assert cfg.spacing == 16

    def test_env_overrides_spacing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_CROSSHATCH_SPACING", "32")
        cfg = crosshatch_config_from_env()
        assert cfg.spacing == 32

    def test_env_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_CROSSHATCH_ENABLED", "false")
        cfg = crosshatch_config_from_env()
        assert cfg.enabled is False
