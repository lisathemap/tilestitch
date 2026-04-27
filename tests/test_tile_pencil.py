import pytest
from PIL import Image

from tilestitch.tile_pencil import (
    PencilConfig,
    PencilError,
    apply_pencil,
    pencil_config_from_env,
)


def _solid(colour: tuple[int, int, int] = (120, 80, 40)) -> Image.Image:
    img = Image.new("RGB", (64, 64), colour)
    return img


class TestPencilConfig:
    def test_defaults(self) -> None:
        cfg = PencilConfig()
        assert cfg.enabled is True
        assert cfg.blur_radius == 2.0
        assert cfg.blend == 0.85

    def test_blur_radius_stored(self) -> None:
        cfg = PencilConfig(blur_radius=3.5)
        assert cfg.blur_radius == 3.5

    def test_blend_stored(self) -> None:
        cfg = PencilConfig(blend=0.5)
        assert cfg.blend == 0.5

    def test_zero_blur_radius_raises(self) -> None:
        with pytest.raises(PencilError, match="blur_radius"):
            PencilConfig(blur_radius=0.0)

    def test_negative_blur_radius_raises(self) -> None:
        with pytest.raises(PencilError, match="blur_radius"):
            PencilConfig(blur_radius=-1.0)

    def test_blend_above_one_raises(self) -> None:
        with pytest.raises(PencilError, match="blend"):
            PencilConfig(blend=1.1)

    def test_blend_below_zero_raises(self) -> None:
        with pytest.raises(PencilError, match="blend"):
            PencilConfig(blend=-0.1)

    def test_blend_zero_valid(self) -> None:
        cfg = PencilConfig(blend=0.0)
        assert cfg.blend == 0.0

    def test_blend_one_valid(self) -> None:
        cfg = PencilConfig(blend=1.0)
        assert cfg.blend == 1.0


class TestApplyPencil:
    def test_returns_image(self) -> None:
        result = apply_pencil(_solid(), PencilConfig())
        assert isinstance(result, Image.Image)

    def test_output_size_unchanged(self) -> None:
        img = _solid()
        result = apply_pencil(img, PencilConfig())
        assert result.size == img.size

    def test_disabled_returns_original(self) -> None:
        img = _solid()
        cfg = PencilConfig(enabled=False)
        result = apply_pencil(img, cfg)
        assert result is img

    def test_output_is_rgba(self) -> None:
        result = apply_pencil(_solid(), PencilConfig())
        assert result.mode == "RGBA"

    def test_high_blend_produces_different_image(self) -> None:
        img = _solid((200, 100, 50))
        result = apply_pencil(img, PencilConfig(blend=1.0))
        assert list(result.getdata()) != list(img.convert("RGBA").getdata())


class TestPencilConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for key in (
            "TILESTITCH_PENCIL_ENABLED",
            "TILESTITCH_PENCIL_BLUR_RADIUS",
            "TILESTITCH_PENCIL_BLEND",
        ):
            monkeypatch.delenv(key, raising=False)
        cfg = pencil_config_from_env()
        assert cfg.enabled is True
        assert cfg.blur_radius == 2.0
        assert cfg.blend == 0.85

    def test_env_overrides(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TILESTITCH_PENCIL_ENABLED", "false")
        monkeypatch.setenv("TILESTITCH_PENCIL_BLUR_RADIUS", "4.0")
        monkeypatch.setenv("TILESTITCH_PENCIL_BLEND", "0.6")
        cfg = pencil_config_from_env()
        assert cfg.enabled is False
        assert cfg.blur_radius == 4.0
        assert cfg.blend == 0.6
