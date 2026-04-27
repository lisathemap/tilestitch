import pytest
from PIL import Image

from tilestitch.tile_pencil import PencilConfig
from tilestitch.pencil_pipeline import PencilStage, build_pencil_stage


def _blank() -> Image.Image:
    return Image.new("RGB", (32, 32), (180, 180, 180))


class TestPencilStage:
    def test_returns_same_image_when_config_none(self) -> None:
        img = _blank()
        stage = PencilStage(config=None)
        result = stage.process(img)
        assert result is img

    def test_returns_same_image_when_disabled(self) -> None:
        img = _blank()
        stage = PencilStage(config=PencilConfig(enabled=False))
        result = stage.process(img)
        assert result is img

    def test_returns_image_when_enabled(self) -> None:
        img = _blank()
        stage = PencilStage(config=PencilConfig(enabled=True))
        result = stage.process(img)
        assert isinstance(result, Image.Image)

    def test_output_size_matches_input(self) -> None:
        img = _blank()
        stage = PencilStage(config=PencilConfig())
        result = stage.process(img)
        assert result.size == img.size

    def test_build_pencil_stage_returns_stage(self) -> None:
        stage = build_pencil_stage(PencilConfig())
        assert isinstance(stage, PencilStage)

    def test_build_pencil_stage_none_config(self) -> None:
        stage = build_pencil_stage(None)
        img = _blank()
        assert stage.process(img) is img
