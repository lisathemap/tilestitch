"""Tests for tilestitch.tile_despeckle and tilestitch.despeckle_pipeline."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_despeckle import (
    DespeckleConfig,
    DespeckleError,
    apply_despeckle,
    despeckle_config_from_env,
)
from tilestitch.despeckle_pipeline import DespeckleStage, build_despeckle_stage


def _solid(colour: tuple[int, int, int, int] = (120, 80, 60, 255)) -> Image.Image:
    img = Image.new("RGBA", (64, 64), colour)
    return img


# ---------------------------------------------------------------------------
# DespeckleConfig
# ---------------------------------------------------------------------------

class TestDespeckleConfig:
    def test_defaults(self) -> None:
        cfg = DespeckleConfig()
        assert cfg.enabled is True
        assert cfg.iterations == 1

    def test_iterations_stored(self) -> None:
        cfg = DespeckleConfig(iterations=3)
        assert cfg.iterations == 3

    def test_zero_iterations_raises(self) -> None:
        with pytest.raises(DespeckleError):
            DespeckleConfig(iterations=0)

    def test_negative_iterations_raises(self) -> None:
        with pytest.raises(DespeckleError):
            DespeckleConfig(iterations=-1)

    def test_invalid_enabled_raises(self) -> None:
        with pytest.raises(DespeckleError):
            DespeckleConfig(enabled="yes")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# despeckle_config_from_env
# ---------------------------------------------------------------------------

class TestDespeckleConfigFromEnv:
    def test_defaults_from_empty_env(self) -> None:
        cfg = despeckle_config_from_env({})
        assert cfg.enabled is True
        assert cfg.iterations == 1

    def test_disabled_via_env(self) -> None:
        cfg = despeckle_config_from_env({"TILESTITCH_DESPECKLE_ENABLED": "false"})
        assert cfg.enabled is False

    def test_iterations_from_env(self) -> None:
        cfg = despeckle_config_from_env({"TILESTITCH_DESPECKLE_ITERATIONS": "4"})
        assert cfg.iterations == 4

    def test_invalid_iterations_raises(self) -> None:
        with pytest.raises(DespeckleError):
            despeckle_config_from_env({"TILESTITCH_DESPECKLE_ITERATIONS": "abc"})


# ---------------------------------------------------------------------------
# apply_despeckle
# ---------------------------------------------------------------------------

class TestApplyDespeckle:
    def test_returns_image(self) -> None:
        img = _solid()
        result = apply_despeckle(img, DespeckleConfig())
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self) -> None:
        img = _solid()
        result = apply_despeckle(img, DespeckleConfig())
        assert result.size == img.size

    def test_disabled_returns_original(self) -> None:
        img = _solid()
        result = apply_despeckle(img, DespeckleConfig(enabled=False))
        assert result is img

    def test_multiple_iterations(self) -> None:
        img = _solid()
        result = apply_despeckle(img, DespeckleConfig(iterations=3))
        assert result.size == img.size


# ---------------------------------------------------------------------------
# DespeckleStage / build_despeckle_stage
# ---------------------------------------------------------------------------

class TestDespeckleStage:
    def test_returns_same_image_when_config_none(self) -> None:
        stage = DespeckleStage(config=None)
        img = _solid()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self) -> None:
        stage = DespeckleStage(config=DespeckleConfig(enabled=False))
        img = _solid()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self) -> None:
        stage = build_despeckle_stage(DespeckleConfig(iterations=1))
        img = _solid()
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_build_with_none_uses_defaults(self) -> None:
        stage = build_despeckle_stage(None)
        assert stage.config is not None
        assert stage.config.enabled is True
