"""Tests for tilestitch.noise_pipeline."""
from PIL import Image

from tilestitch.noise_pipeline import NoiseStage, build_noise_stage
from tilestitch.tile_noise import NoiseConfig


def _blank(size: int = 64) -> Image.Image:
    return Image.new("RGB", (size, size), (200, 200, 200))


class TestNoiseStage:
    def test_returns_same_image_when_config_none(self):
        stage = NoiseStage(config=None)
        img = _blank()
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        stage = NoiseStage(config=NoiseConfig(enabled=False))
        img = _blank()
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        stage = NoiseStage(config=NoiseConfig(enabled=True, radius=1))
        img = _blank()
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_output_size_matches_input(self):
        stage = NoiseStage(config=NoiseConfig(enabled=True, radius=1))
        img = _blank(size=128)
        result = stage.process(img)
        assert result.size == (128, 128)


class TestBuildNoiseStage:
    def test_returns_noise_stage(self):
        stage = build_noise_stage(NoiseConfig())
        assert isinstance(stage, NoiseStage)

    def test_config_stored(self):
        cfg = NoiseConfig(enabled=True, radius=2)
        stage = build_noise_stage(cfg)
        assert stage.config is cfg

    def test_builds_from_env_when_config_none(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_NOISE_ENABLED", raising=False)
        monkeypatch.delenv("TILESTITCH_NOISE_RADIUS", raising=False)
        stage = build_noise_stage()
        assert isinstance(stage, NoiseStage)
        assert stage.config is not None
