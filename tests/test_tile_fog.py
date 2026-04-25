"""Tests for tilestitch.tile_fog."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_fog import FogConfig, FogError, apply_fog


def _solid(colour: tuple[int, int, int] = (100, 150, 200), size: int = 64) -> Image.Image:
    return Image.new("RGB", (size, size), colour)


class TestFogConfig:
    def test_defaults(self) -> None:
        cfg = FogConfig()
        assert cfg.enabled is True
        assert cfg.density == pytest.approx(0.4)
        assert cfg.colour == "#ffffff"

    def test_density_stored(self) -> None:
        cfg = FogConfig(density=0.7)
        assert cfg.density == pytest.approx(0.7)

    def test_zero_density_raises(self) -> None:
        with pytest.raises(FogError, match="density"):
            FogConfig(density=0.0)

    def test_negative_density_raises(self) -> None:
        with pytest.raises(FogError, match="density"):
            FogConfig(density=-0.1)

    def test_density_above_one_raises(self) -> None:
        with pytest.raises(FogError, match="density"):
            FogConfig(density=1.1)

    def test_density_one_valid(self) -> None:
        cfg = FogConfig(density=1.0)
        assert cfg.density == pytest.approx(1.0)

    def test_invalid_colour_raises(self) -> None:
        with pytest.raises(FogError, match="colour"):
            FogConfig(colour="not-a-colour")

    def test_empty_colour_raises(self) -> None:
        with pytest.raises(FogError, match="colour"):
            FogConfig(colour="")

    def test_custom_colour_stored(self) -> None:
        cfg = FogConfig(colour="#aabbcc")
        assert cfg.colour == "#aabbcc"

    def test_invalid_enabled_raises(self) -> None:
        with pytest.raises(FogError, match="enabled"):
            FogConfig(enabled="yes")  # type: ignore[arg-type]


class TestApplyFog:
    def test_returns_image(self) -> None:
        img = _solid()
        result = apply_fog(img, FogConfig())
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self) -> None:
        img = _solid(size=64)
        result = apply_fog(img, FogConfig())
        assert result.size == img.size

    def test_mode_preserved_rgb(self) -> None:
        img = _solid()
        result = apply_fog(img, FogConfig())
        assert result.mode == "RGB"

    def test_disabled_returns_same_object(self) -> None:
        img = _solid()
        cfg = FogConfig(enabled=False)
        result = apply_fog(img, cfg)
        assert result is img

    def test_full_density_whitens_image(self) -> None:
        img = _solid(colour=(0, 0, 0))
        result = apply_fog(img, FogConfig(density=1.0, colour="#ffffff"))
        px = result.getpixel((32, 32))
        assert px[0] > 200 and px[1] > 200 and px[2] > 200

    def test_rgba_input_preserved(self) -> None:
        img = Image.new("RGBA", (32, 32), (50, 100, 150, 255))
        result = apply_fog(img, FogConfig())
        assert result.mode == "RGBA"
