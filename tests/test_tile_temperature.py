"""Tests for tilestitch.tile_temperature."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_temperature import (
    TemperatureConfig,
    TemperatureError,
    apply_temperature,
)


def _solid(r: int, g: int, b: int, size: int = 4) -> Image.Image:
    img = Image.new("RGB", (size, size), (r, g, b))
    return img


# ---------------------------------------------------------------------------
# TemperatureConfig
# ---------------------------------------------------------------------------

class TestTemperatureConfig:
    def test_defaults(self):
        cfg = TemperatureConfig()
        assert cfg.enabled is False
        assert cfg.shift == 0.0

    def test_shift_stored(self):
        cfg = TemperatureConfig(shift=0.5)
        assert cfg.shift == 0.5

    def test_shift_zero_valid(self):
        cfg = TemperatureConfig(shift=0.0)
        assert cfg.shift == 0.0

    def test_shift_one_valid(self):
        cfg = TemperatureConfig(shift=1.0)
        assert cfg.shift == 1.0

    def test_shift_minus_one_valid(self):
        cfg = TemperatureConfig(shift=-1.0)
        assert cfg.shift == -1.0

    def test_shift_above_one_raises(self):
        with pytest.raises(TemperatureError):
            TemperatureConfig(shift=1.1)

    def test_shift_below_minus_one_raises(self):
        with pytest.raises(TemperatureError):
            TemperatureConfig(shift=-1.1)

    def test_enabled_stored(self):
        cfg = TemperatureConfig(enabled=True, shift=0.3)
        assert cfg.enabled is True


# ---------------------------------------------------------------------------
# apply_temperature
# ---------------------------------------------------------------------------

class TestApplyTemperature:
    def test_returns_image_when_disabled(self):
        img = _solid(128, 128, 128)
        cfg = TemperatureConfig(enabled=False, shift=0.5)
        result = apply_temperature(img, cfg)
        assert result is img

    def test_returns_image_when_shift_zero(self):
        img = _solid(128, 128, 128)
        cfg = TemperatureConfig(enabled=True, shift=0.0)
        result = apply_temperature(img, cfg)
        assert result is img

    def test_warm_shift_increases_red(self):
        img = _solid(100, 128, 200)
        cfg = TemperatureConfig(enabled=True, shift=1.0)
        result = apply_temperature(img, cfg)
        px = result.convert("RGB").getpixel((0, 0))
        assert px[0] >= 100  # red increased or clamped

    def test_warm_shift_decreases_blue(self):
        img = _solid(100, 128, 200)
        cfg = TemperatureConfig(enabled=True, shift=1.0)
        result = apply_temperature(img, cfg)
        px = result.convert("RGB").getpixel((0, 0))
        assert px[2] <= 200  # blue decreased or clamped

    def test_cool_shift_increases_blue(self):
        img = _solid(200, 128, 100)
        cfg = TemperatureConfig(enabled=True, shift=-1.0)
        result = apply_temperature(img, cfg)
        px = result.convert("RGB").getpixel((0, 0))
        assert px[2] >= 100

    def test_cool_shift_decreases_red(self):
        img = _solid(200, 128, 100)
        cfg = TemperatureConfig(enabled=True, shift=-1.0)
        result = apply_temperature(img, cfg)
        px = result.convert("RGB").getpixel((0, 0))
        assert px[0] <= 200

    def test_rgba_input_preserved(self):
        img = Image.new("RGBA", (4, 4), (100, 128, 200, 180))
        cfg = TemperatureConfig(enabled=True, shift=0.5)
        result = apply_temperature(img, cfg)
        assert result.mode == "RGBA"

    def test_rgb_input_preserved(self):
        img = _solid(100, 128, 200)
        cfg = TemperatureConfig(enabled=True, shift=0.5)
        result = apply_temperature(img, cfg)
        assert result.mode == "RGB"

    def test_pixel_values_clamped(self):
        img = _solid(255, 128, 0)
        cfg = TemperatureConfig(enabled=True, shift=1.0)
        result = apply_temperature(img, cfg)
        px = result.convert("RGB").getpixel((0, 0))
        assert 0 <= px[0] <= 255
        assert 0 <= px[2] <= 255
