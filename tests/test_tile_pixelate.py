import pytest
from PIL import Image

from tilestitch.tile_pixelate import (
    PixelateConfig,
    PixelateError,
    apply_pixelate,
    pixelate_config_from_env,
)
from tilestitch.pixelate_pipeline import PixelateStage, build_pixelate_stage


def _solid(colour=(100, 150, 200), size=(64, 64)) -> Image.Image:
    img = Image.new("RGB", size, colour)
    return img


class TestPixelateConfig:
    def test_defaults(self):
        cfg = PixelateConfig()
        assert cfg.block_size == 8
        assert cfg.enabled is True

    def test_block_size_stored(self):
        cfg = PixelateConfig(block_size=16)
        assert cfg.block_size == 16

    def test_zero_block_size_raises(self):
        with pytest.raises(PixelateError):
            PixelateConfig(block_size=0)

    def test_negative_block_size_raises(self):
        with pytest.raises(PixelateError):
            PixelateConfig(block_size=-1)

    def test_block_size_256_valid(self):
        cfg = PixelateConfig(block_size=256)
        assert cfg.block_size == 256

    def test_block_size_257_raises(self):
        with pytest.raises(PixelateError):
            PixelateConfig(block_size=257)

    def test_enabled_false_stored(self):
        cfg = PixelateConfig(enabled=False)
        assert cfg.enabled is False


class TestApplyPixelate:
    def test_returns_image(self):
        img = _solid()
        cfg = PixelateConfig(block_size=8)
        result = apply_pixelate(img, cfg)
        assert isinstance(result, Image.Image)

    def test_output_same_size(self):
        img = _solid(size=(64, 64))
        cfg = PixelateConfig(block_size=8)
        result = apply_pixelate(img, cfg)
        assert result.size == (64, 64)

    def test_disabled_returns_original(self):
        img = _solid()
        cfg = PixelateConfig(enabled=False)
        result = apply_pixelate(img, cfg)
        assert result is img

    def test_block_size_1_unchanged_content(self):
        img = _solid(colour=(10, 20, 30), size=(4, 4))
        cfg = PixelateConfig(block_size=1)
        result = apply_pixelate(img, cfg)
        assert result.getpixel((0, 0)) == (10, 20, 30)

    def test_large_block_produces_uniform_region(self):
        img = _solid(colour=(255, 0, 0), size=(32, 32))
        cfg = PixelateConfig(block_size=32)
        result = apply_pixelate(img, cfg)
        pixels = set(result.getpixel((x, y)) for x in range(32) for y in range(32))
        assert len(pixels) == 1


class TestPixelateStage:
    def test_returns_same_image_when_config_none(self):
        img = _solid()
        stage = build_pixelate_stage(config=None)
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        img = _solid()
        cfg = PixelateConfig(enabled=False)
        stage = build_pixelate_stage(config=cfg)
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        img = _solid()
        cfg = PixelateConfig(block_size=4)
        stage = build_pixelate_stage(config=cfg)
        result = stage.process(img)
        assert isinstance(result, Image.Image)
        assert result.size == img.size


class TestPixelateConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_PIXELATE_BLOCK_SIZE", raising=False)
        monkeypatch.delenv("TILESTITCH_PIXELATE_ENABLED", raising=False)
        cfg = pixelate_config_from_env()
        assert cfg.block_size == 8
        assert cfg.enabled is True

    def test_reads_block_size_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_PIXELATE_BLOCK_SIZE", "16")
        cfg = pixelate_config_from_env()
        assert cfg.block_size == 16

    def test_disabled_via_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_PIXELATE_ENABLED", "false")
        cfg = pixelate_config_from_env()
        assert cfg.enabled is False
