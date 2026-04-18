import pytest
from PIL import Image
from tilestitch.tile_sepia import (
    SepiaConfig,
    SepiaError,
    apply_sepia,
    sepia_config_from_env,
)


def _solid(colour=(120, 80, 40, 255), size=(4, 4)) -> Image.Image:
    img = Image.new("RGBA", size, colour)
    return img


class TestSepiaConfig:
    def test_defaults(self):
        cfg = SepiaConfig()
        assert cfg.enabled is True
        assert cfg.intensity == 1.0

    def test_intensity_stored(self):
        cfg = SepiaConfig(intensity=0.5)
        assert cfg.intensity == 0.5

    def test_zero_intensity_valid(self):
        cfg = SepiaConfig(intensity=0.0)
        assert cfg.intensity == 0.0

    def test_intensity_above_one_raises(self):
        with pytest.raises(SepiaError):
            SepiaConfig(intensity=1.1)

    def test_negative_intensity_raises(self):
        with pytest.raises(SepiaError):
            SepiaConfig(intensity=-0.1)

    def test_invalid_enabled_raises(self):
        with pytest.raises(SepiaError):
            SepiaConfig(enabled="yes")  # type: ignore


class TestApplySepia:
    def test_returns_image(self):
        img = _solid()
        result = apply_sepia(img, SepiaConfig())
        assert isinstance(result, Image.Image)

    def test_output_size_preserved(self):
        img = _solid(size=(8, 6))
        result = apply_sepia(img, SepiaConfig())
        assert result.size == (8, 6)

    def test_output_mode_is_rgba(self):
        img = _solid()
        result = apply_sepia(img, SepiaConfig())
        assert result.mode == "RGBA"

    def test_disabled_returns_same_object(self):
        img = _solid()
        result = apply_sepia(img, SepiaConfig(enabled=False))
        assert result is img

    def test_zero_intensity_preserves_pixels(self):
        colour = (100, 150, 200, 255)
        img = _solid(colour=colour)
        result = apply_sepia(img, SepiaConfig(intensity=0.0))
        px = result.getpixel((0, 0))
        assert px == colour

    def test_full_sepia_changes_pixels(self):
        img = _solid(colour=(100, 100, 100, 255))
        result = apply_sepia(img, SepiaConfig(intensity=1.0))
        px = result.getpixel((0, 0))
        assert px != (100, 100, 100, 255)

    def test_alpha_preserved(self):
        img = _solid(colour=(80, 80, 80, 128))
        result = apply_sepia(img, SepiaConfig())
        px = result.getpixel((0, 0))
        assert px[3] == 128


class TestSepiaConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_SEPIA_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_SEPIA_INTENSITY", raising=False)
        cfg = sepia_config_from_env()
        assert cfg.enabled is False
        assert cfg.intensity == 1.0

    def test_reads_enabled(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SEPIA_ENABLED", "true")
        cfg = sepia_config_from_env()
        assert cfg.enabled is True

    def test_reads_intensity(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_SEPIA_INTENSITY", "0.5")
        cfg = sepia_config_from_env()
        assert cfg.intensity == 0.5
