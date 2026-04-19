import pytest
from PIL import Image
from tilestitch.tile_denoise import (
    DenoiseConfig,
    DenoiseError,
    apply_denoise,
    denoise_config_from_env,
)
from tilestitch.denoise_pipeline import DenoiseStage, build_denoise_stage


def _solid(colour=(120, 80, 60, 255), size=(16, 16)) -> Image.Image:
    img = Image.new("RGBA", size, colour)
    return img


class TestDenoiseConfig:
    def test_defaults(self):
        cfg = DenoiseConfig()
        assert cfg.enabled is True
        assert cfg.iterations == 1

    def test_iterations_stored(self):
        cfg = DenoiseConfig(iterations=3)
        assert cfg.iterations == 3

    def test_zero_iterations_raises(self):
        with pytest.raises(DenoiseError):
            DenoiseConfig(iterations=0)

    def test_negative_iterations_raises(self):
        with pytest.raises(DenoiseError):
            DenoiseConfig(iterations=-1)

    def test_iterations_above_max_raises(self):
        with pytest.raises(DenoiseError):
            DenoiseConfig(iterations=11)

    def test_max_iterations_valid(self):
        cfg = DenoiseConfig(iterations=10)
        assert cfg.iterations == 10

    def test_invalid_enabled_raises(self):
        with pytest.raises(DenoiseError):
            DenoiseConfig(enabled="yes")  # type: ignore


class TestApplyDenoise:
    def test_returns_image(self):
        img = _solid()
        cfg = DenoiseConfig()
        result = apply_denoise(img, cfg)
        assert isinstance(result, Image.Image)

    def test_output_same_size(self):
        img = _solid(size=(32, 32))
        cfg = DenoiseConfig()
        result = apply_denoise(img, cfg)
        assert result.size == img.size

    def test_disabled_returns_original(self):
        img = _solid()
        cfg = DenoiseConfig(enabled=False)
        result = apply_denoise(img, cfg)
        assert result is img

    def test_multiple_iterations_run(self):
        img = _solid(size=(16, 16))
        cfg = DenoiseConfig(iterations=3)
        result = apply_denoise(img, cfg)
        assert result.size == img.size

    def test_rgb_mode_preserved(self):
        img = Image.new("RGB", (16, 16), (100, 150, 200))
        cfg = DenoiseConfig()
        result = apply_denoise(img, cfg)
        assert result.mode == "RGB"


class TestDenoiseStage:
    def test_returns_same_image_when_config_none(self):
        img = _solid()
        stage = DenoiseStage(config=None)
        assert stage.process(img) is img

    def test_returns_same_image_when_disabled(self):
        img = _solid()
        stage = DenoiseStage(config=DenoiseConfig(enabled=False))
        assert stage.process(img) is img

    def test_returns_image_when_enabled(self):
        img = _solid()
        stage = DenoiseStage(config=DenoiseConfig())
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_build_denoise_stage_returns_stage(self):
        stage = build_denoise_stage(DenoiseConfig())
        assert isinstance(stage, DenoiseStage)

    def test_build_denoise_stage_uses_env_when_no_config(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_DENOISE_ITERATIONS", "2")
        stage = build_denoise_stage()
        assert stage.config.iterations == 2
