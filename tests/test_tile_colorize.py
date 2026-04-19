import pytest
from PIL import Image

from tilestitch.tile_colorize import (
    ColorizeConfig,
    ColorizeError,
    apply_colorize,
    colorize_config_from_env,
)
from tilestitch.colorize_pipeline import ColorizeStage, build_colorize_stage


def _solid(colour: tuple, size: tuple = (4, 4), mode: str = "RGB") -> Image.Image:
    img = Image.new(mode, size, colour)
    return img


class TestColorizeConfig:
    def test_defaults(self):
        cfg = ColorizeConfig()
        assert cfg.black == "#000000"
        assert cfg.white == "#ffffff"
        assert cfg.enabled is True

    def test_custom_colours_stored(self):
        cfg = ColorizeConfig(black="#112233", white="#aabbcc")
        assert cfg.black == "#112233"
        assert cfg.white == "#aabbcc"

    def test_invalid_black_raises(self):
        with pytest.raises(ColorizeError):
            ColorizeConfig(black="notacolour")

    def test_invalid_white_raises(self):
        with pytest.raises(ColorizeError):
            ColorizeConfig(white="bad")

    def test_short_hex_valid(self):
        cfg = ColorizeConfig(black="#000", white="#fff")
        assert cfg.black == "#000"

    def test_invalid_enabled_raises(self):
        with pytest.raises(ColorizeError):
            ColorizeConfig(enabled="yes")  # type: ignore


class TestApplyColorize:
    def test_returns_image(self):
        img = _solid((128, 128, 128))
        cfg = ColorizeConfig()
        result = apply_colorize(img, cfg)
        assert isinstance(result, Image.Image)

    def test_disabled_returns_original(self):
        img = _solid((100, 150, 200))
        cfg = ColorizeConfig(enabled=False)
        result = apply_colorize(img, cfg)
        assert result is img

    def test_rgba_preserves_alpha(self):
        img = Image.new("RGBA", (4, 4), (100, 100, 100, 128))
        cfg = ColorizeConfig()
        result = apply_colorize(img, cfg)
        assert result.mode == "RGBA"
        assert result.getpixel((0, 0))[3] == 128

    def test_output_size_unchanged(self):
        img = _solid((80, 80, 80), size=(10, 10))
        cfg = ColorizeConfig()
        result = apply_colorize(img, cfg)
        assert result.size == (10, 10)


class TestColorizeStage:
    def test_returns_same_image_when_config_none(self):
        img = _solid((50, 50, 50))
        stage = build_colorize_stage(None)
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        img = _solid((50, 50, 50))
        cfg = ColorizeConfig(enabled=False)
        stage = build_colorize_stage(cfg)
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        img = _solid((100, 100, 100))
        cfg = ColorizeConfig()
        stage = build_colorize_stage(cfg)
        result = stage.process(img)
        assert isinstance(result, Image.Image)


def test_colorize_config_from_env(monkeypatch):
    monkeypatch.setenv("TILESTITCH_COLORIZE_BLACK", "#111111")
    monkeypatch.setenv("TILESTITCH_COLORIZE_WHITE", "#eeeeee")
    monkeypatch.setenv("TILESTITCH_COLORIZE_ENABLED", "true")
    cfg = colorize_config_from_env()
    assert cfg.black == "#111111"
    assert cfg.white == "#eeeeee"
    assert cfg.enabled is True
