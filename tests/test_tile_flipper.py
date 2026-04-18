"""Tests for tilestitch.tile_flipper and tilestitch.flip_pipeline."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_flipper import (
    FlipAxis,
    FlipConfig,
    FlipError,
    flip_image,
)
from tilestitch.flip_pipeline import FlipStage, build_flip_stage


def _solid(width: int = 4, height: int = 4) -> Image.Image:
    img = Image.new("RGB", (width, height), color=(255, 0, 0))
    # Paint left column blue so flips are detectable
    for y in range(height):
        img.putpixel((0, y), (0, 0, 255))
    return img


class TestFlipAxisFromString:
    def test_horizontal(self):
        assert FlipAxis.from_string("horizontal") is FlipAxis.HORIZONTAL

    def test_vertical(self):
        assert FlipAxis.from_string("vertical") is FlipAxis.VERTICAL

    def test_both(self):
        assert FlipAxis.from_string("both") is FlipAxis.BOTH

    def test_case_insensitive(self):
        assert FlipAxis.from_string("HORIZONTAL") is FlipAxis.HORIZONTAL

    def test_whitespace_stripped(self):
        assert FlipAxis.from_string("  vertical  ") is FlipAxis.VERTICAL

    def test_unknown_raises(self):
        with pytest.raises(FlipError):
            FlipAxis.from_string("diagonal")


class TestFlipConfig:
    def test_defaults(self):
        cfg = FlipConfig()
        assert cfg.enabled is False
        assert cfg.axis is FlipAxis.HORIZONTAL

    def test_invalid_axis_raises(self):
        with pytest.raises(FlipError):
            FlipConfig(axis="horizontal")  # type: ignore[arg-type]


class TestFlipImage:
    def test_disabled_returns_same_object(self):
        img = _solid()
        cfg = FlipConfig(enabled=False)
        assert flip_image(img, cfg) is img

    def test_horizontal_moves_blue_column_to_right(self):
        img = _solid(4, 4)
        cfg = FlipConfig(enabled=True, axis=FlipAxis.HORIZONTAL)
        result = flip_image(img, cfg)
        assert result.getpixel((3, 0)) == (0, 0, 255)
        assert result.getpixel((0, 0)) == (255, 0, 0)

    def test_vertical_preserves_blue_column_position(self):
        img = _solid(4, 4)
        cfg = FlipConfig(enabled=True, axis=FlipAxis.VERTICAL)
        result = flip_image(img, cfg)
        # Left column should still be blue after vertical flip
        assert result.getpixel((0, 0)) == (0, 0, 255)

    def test_both_flips_applied(self):
        img = _solid(4, 4)
        cfg = FlipConfig(enabled=True, axis=FlipAxis.BOTH)
        result = flip_image(img, cfg)
        # Blue column ends up on the right
        assert result.getpixel((3, 0)) == (0, 0, 255)


class TestFlipStage:
    def test_returns_same_when_disabled(self):
        img = _solid()
        stage = FlipStage(config=FlipConfig(enabled=False))
        assert stage.process(img) is img

    def test_returns_same_when_config_none(self):
        img = _solid()
        stage = FlipStage(config=None)
        assert stage.process(img) is img

    def test_returns_flipped_image(self):
        img = _solid(4, 4)
        stage = FlipStage(config=FlipConfig(enabled=True, axis=FlipAxis.HORIZONTAL))
        result = stage.process(img)
        assert result.getpixel((3, 0)) == (0, 0, 255)

    def test_build_flip_stage_returns_stage(self):
        cfg = FlipConfig(enabled=False)
        stage = build_flip_stage(cfg)
        assert isinstance(stage, FlipStage)
