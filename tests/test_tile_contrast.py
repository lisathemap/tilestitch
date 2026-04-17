import pytest
from PIL import Image

from tilestitch.tile_contrast import (
    ContrastConfig,
    ContrastError,
    adjust_contrast,
    contrast_config_from_env,
)


def _solid(color=(128, 128, 128)) -> Image.Image:
    img = Image.new("RGB", (4, 4), color)
    return img


class TestContrastConfig:
    def test_defaults(self):
        cfg = ContrastConfig()
        assert cfg.enabled is False
        assert cfg.factor == 1.0

    def test_zero_factor_raises(self):
        with pytest.raises(ContrastError):
            ContrastConfig(factor=0.0)

    def test_negative_factor_raises(self):
        with pytest.raises(ContrastError):
            ContrastConfig(factor=-0.5)

    def test_positive_factor_ok(self):
        cfg = ContrastConfig(factor=2.0)
        assert cfg.factor == 2.0


class TestAdjustContrast:
    def test_returns_image(self):
        img = _solid()
        cfg = ContrastConfig(enabled=True, factor=1.5)
        result = adjust_contrast(img, cfg)
        assert isinstance(result, Image.Image)

    def test_disabled_returns_same_object(self):
        img = _solid()
        cfg = ContrastConfig(enabled=False, factor=2.0)
        result = adjust_contrast(img, cfg)
        assert result is img

    def test_factor_one_returns_same_object(self):
        img = _solid()
        cfg = ContrastConfig(enabled=True, factor=1.0)
        result = adjust_contrast(img, cfg)
        assert result is img

    def test_size_preserved(self):
        img = _solid()
        cfg = ContrastConfig(enabled=True, factor=2.0)
        result = adjust_contrast(img, cfg)
        assert result.size == img.size


class TestContrastConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_CONTRAST_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_CONTRAST_FACTOR", raising=False)
        cfg = contrast_config_from_env()
        assert cfg.enabled is False
        assert cfg.factor == 1.0

    def test_reads_enabled(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_CONTRAST_ENABLED", "true")
        monkeypatch.setenv("TILESTITCH_CONTRAST_FACTOR", "1.8")
        cfg = contrast_config_from_env()
        assert cfg.enabled is True
        assert cfg.factor == pytest.approx(1.8)
