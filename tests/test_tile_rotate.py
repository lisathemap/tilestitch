import pytest
from PIL import Image

from tilestitch.tile_rotate import RotateConfig, RotateError, rotate_image


def _solid(color: str = "red", size: int = 64) -> Image.Image:
    return Image.new("RGB", (size, size), color)


class TestRotateConfig:
    def test_defaults(self):
        cfg = RotateConfig()
        assert cfg.angle == 0.0
        assert cfg.expand is True
        assert cfg.fill_color == "white"

    def test_angle_stored(self):
        cfg = RotateConfig(angle=45.0)
        assert cfg.angle == 45.0

    def test_negative_angle_valid(self):
        cfg = RotateConfig(angle=-90.0)
        assert cfg.angle == -90.0

    def test_angle_too_large_raises(self):
        with pytest.raises(RotateError):
            RotateConfig(angle=361.0)

    def test_angle_too_small_raises(self):
        with pytest.raises(RotateError):
            RotateConfig(angle=-361.0)

    def test_boundary_360_valid(self):
        cfg = RotateConfig(angle=360.0)
        assert cfg.angle == 360.0

    def test_string_angle_coerced(self):
        cfg = RotateConfig(angle="30.0")  # type: ignore[arg-type]
        assert cfg.angle == 30.0


class TestRotateImage:
    def test_zero_angle_returns_same(self):
        img = _solid()
        cfg = RotateConfig(angle=0.0)
        result = rotate_image(img, cfg)
        assert result is img

    def test_90_degree_rotation_swaps_dims_with_expand(self):
        img = Image.new("RGB", (100, 50), "blue")
        cfg = RotateConfig(angle=90.0, expand=True)
        result = rotate_image(img, cfg)
        assert result.size == (50, 100)

    def test_no_expand_keeps_size(self):
        img = _solid(size=64)
        cfg = RotateConfig(angle=45.0, expand=False)
        result = rotate_image(img, cfg)
        assert result.size == (64, 64)

    def test_returns_image(self):
        img = _solid()
        cfg = RotateConfig(angle=15.0)
        result = rotate_image(img, cfg)
        assert isinstance(result, Image.Image)
