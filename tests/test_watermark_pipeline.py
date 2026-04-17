"""Tests for tilestitch.watermark_pipeline."""
from PIL import Image

from tilestitch.tile_watermark import WatermarkConfig
from tilestitch.watermark_pipeline import WatermarkStage, build_watermark_stage


def _blank() -> Image.Image:
    return Image.new("RGB", (256, 256), (128, 128, 128))


class TestWatermarkStage:
    def test_returns_image_when_enabled(self):
        cfg = WatermarkConfig(text="hello")
        stage = WatermarkStage(config=cfg, enabled=True)
        result = stage.process(_blank())
        assert isinstance(result, Image.Image)

    def test_returns_same_image_when_disabled(self):
        cfg = WatermarkConfig(text="hello")
        stage = WatermarkStage(config=cfg, enabled=False)
        img = _blank()
        result = stage.process(img)
        assert result is img

    def test_returns_same_image_when_config_none(self):
        stage = WatermarkStage(config=None, enabled=True)
        img = _blank()
        result = stage.process(img)
        assert result is img

    def test_output_size_unchanged(self):
        cfg = WatermarkConfig(text="tilestitch")
        stage = WatermarkStage(config=cfg, enabled=True)
        img = _blank()
        result = stage.process(img)
        assert result.size == img.size


class TestBuildWatermarkStage:
    def test_no_text_gives_disabled_stage(self):
        stage = build_watermark_stage(text=None)
        assert not stage.enabled
        assert stage.config is None

    def test_with_text_gives_enabled_stage(self):
        stage = build_watermark_stage(text="© OSM")
        assert stage.enabled
        assert stage.config is not None
        assert stage.config.text == "© OSM"

    def test_kwargs_forwarded_to_config(self):
        stage = build_watermark_stage(text="hi", opacity=0.9, font_size=20)
        assert stage.config.opacity == 0.9
        assert stage.config.font_size == 20

    def test_disabled_flag_respected(self):
        stage = build_watermark_stage(text="hi", enabled=False)
        assert not stage.enabled

    def test_process_no_text_returns_original(self):
        stage = build_watermark_stage()
        img = _blank()
        assert stage.process(img) is img
