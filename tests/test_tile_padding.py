import pytest
from PIL import Image

from tilestitch.tile_padding import (
    PaddingConfig,
    PaddingError,
    apply_padding,
    padding_config_from_env,
)
from tilestitch.padding_pipeline import PaddingStage, build_padding_stage


def _blank(width: int = 10, height: int = 10) -> Image.Image:
    return Image.new("RGB", (width, height), color="blue")


class TestPaddingConfig:
    def test_defaults(self):
        cfg = PaddingConfig()
        assert cfg.top == 0
        assert cfg.right == 0
        assert cfg.bottom == 0
        assert cfg.left == 0
        assert cfg.color == "white"

    def test_any_set_false_by_default(self):
        assert not PaddingConfig().any_set

    def test_any_set_true_when_top(self):
        assert PaddingConfig(top=5).any_set

    def test_negative_top_raises(self):
        with pytest.raises(PaddingError):
            PaddingConfig(top=-1)

    def test_negative_left_raises(self):
        with pytest.raises(PaddingError):
            PaddingConfig(left=-3)

    def test_empty_color_raises(self):
        with pytest.raises(PaddingError):
            PaddingConfig(color="")

    def test_whitespace_color_raises(self):
        with pytest.raises(PaddingError):
            PaddingConfig(color="   ")


class TestApplyPadding:
    def test_no_padding_returns_same_size(self):
        img = _blank(10, 10)
        result = apply_padding(img, PaddingConfig())
        assert result.size == (10, 10)

    def test_uniform_padding_increases_size(self):
        img = _blank(10, 10)
        cfg = PaddingConfig(top=5, right=5, bottom=5, left=5)
        result = apply_padding(img, cfg)
        assert result.size == (20, 20)

    def test_asymmetric_padding(self):
        img = _blank(10, 10)
        cfg = PaddingConfig(top=2, right=3, bottom=4, left=1)
        result = apply_padding(img, cfg)
        assert result.size == (14, 16)  # width=10+1+3, height=10+2+4

    def test_invalid_color_raises(self):
        img = _blank()
        cfg = PaddingConfig(top=1, color="notacolor")
        with pytest.raises(PaddingError):
            apply_padding(img, cfg)

    def test_returns_image_instance(self):
        img = _blank()
        result = apply_padding(img, PaddingConfig(top=2))
        assert isinstance(result, Image.Image)


class TestPaddingStage:
    def test_returns_same_image_when_config_none(self):
        img = _blank()
        stage = PaddingStage(config=None)
        assert stage.process(img) is img

    def test_returns_same_image_when_no_padding(self):
        img = _blank()
        stage = PaddingStage(config=PaddingConfig())
        assert stage.process(img) is img

    def test_applies_padding(self):
        img = _blank(10, 10)
        stage = PaddingStage(config=PaddingConfig(top=4, bottom=4))
        result = stage.process(img)
        assert result.size == (10, 18)


class TestBuildPaddingStage:
    def test_returns_padding_stage(self):
        stage = build_padding_stage(PaddingConfig(left=2))
        assert isinstance(stage, PaddingStage)

    def test_uses_provided_config(self):
        cfg = PaddingConfig(right=7)
        stage = build_padding_stage(cfg)
        assert stage.config.right == 7

    def test_env_fallback(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_PADDING_TOP", "3")
        stage = build_padding_stage()
        assert stage.config.top == 3
