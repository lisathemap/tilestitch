"""Tests for tilestitch.tile_colormap."""
import pytest
from PIL import Image

from tilestitch.tile_colormap import (
    ColormapConfig,
    ColormapError,
    apply_colormap,
    list_colormaps,
    colormap_config_from_env,
)


def _grey(width: int = 16, height: int = 16) -> Image.Image:
    img = Image.new("L", (width, height), color=128)
    return img


# --- ColormapConfig ---

class TestColormapConfig:
    def test_defaults(self):
        cfg = ColormapConfig()
        assert cfg.name == "grayscale"
        assert cfg.invert is False

    def test_empty_name_raises(self):
        with pytest.raises(ColormapError):
            ColormapConfig(name="")

    def test_whitespace_name_raises(self):
        with pytest.raises(ColormapError):
            ColormapConfig(name="   ")

    def test_custom_name_stored(self):
        cfg = ColormapConfig(name="viridis")
        assert cfg.name == "viridis"

    def test_invert_stored(self):
        cfg = ColormapConfig(invert=True)
        assert cfg.invert is True


# --- list_colormaps ---

def test_list_colormaps_returns_list():
    result = list_colormaps()
    assert isinstance(result, list)


def test_list_colormaps_includes_viridis():
    assert "viridis" in list_colormaps()


def test_list_colormaps_includes_grayscale():
    assert "grayscale" in list_colormaps()


def test_list_colormaps_nonempty():
    """list_colormaps should always return at least one entry."""
    assert len(list_colormaps()) > 0


def test_list_colormaps_all_strings():
    """Every entry returned by list_colormaps should be a non-empty string."""
    for name in list_colormaps():
        assert isinstance(name, str) and name.strip() != ""


# --- apply_colormap ---

class TestApplyColormap:
    def test_returns_rgb_image(self):
        result = apply_colormap(_grey(), ColormapConfig(name="grayscale"))
        assert result.mode == "RGB"

    def test_output_size_preserved(self):
        img = _grey(32, 64)
        result = apply_colormap(img, ColormapConfig(name="viridis"))
        assert result.size == (32, 64)

    def test_rgb_input_accepted(self):
        img = Image.new("RGB", (16, 16), (100, 100, 100))
        result = apply_colormap(img, ColormapConfig(name="hot"))
        assert result.mode == "RGB"

    def test_unknown_colormap_raises(self):
        with pytest.raises(ColormapError, match="Unknown colormap"):
            apply_colormap(_grey(), ColormapConfig.__new__(ColormapConfig))

    def test_unknown_name_string_raises(self):
        cfg = object.__setattr__(ColormapConfig.__new__(ColormapConfig), '__dict__', {})
        with pytest.raises((ColormapError, Exception)):
            apply_colormap(_grey(), ColormapConfig(name="nonexistent_xyz"))

    def test_viridis_applied(self):
        result = apply_colormap(_grey(), ColormapConfig(name="viridis"))
        assert result is not None

    def test_invert_changes_output(self):
        """Applying a colormap with invert=True should produce different pixels
        than invert=False for a non-uniform image."""
        img = Image.new("L", (16, 16))
        # Create a gradient so inversion has a visible effect
        pixels = list(range(0, 256, 16)) * 16
        img.putdata(pixels[:256])

        normal = apply_colormap(img, ColormapConfig(name="viridis", invert=False))
        inverted = apply_colormap(img, ColormapConfig(name="viridis", invert=True))
        assert list(normal.getdata()) != list(inverted.getdata())


# --- colormap_config_from_env ---

def test_env_defaults(monkeypatch):
    monkeypatch.delenv("TILESTITCH_COLORMAP", raising=False)
    monkeypatch.delenv("TILESTITCH_COLORMAP_INVERT", raising=False)
    cfg = colormap_config_from_env()
    assert cfg.name == "grayscale"
    assert cfg.invert is False


def test_env_name(monkeypatch):
    monkeypatch.setenv("TILESTITCH_COLORMAP", "viridis")
    cfg = colormap_config_from_env()
    assert cfg.name == "viridis"


def test_env_invert_true(monkeypatch):
    monkeypatch.setenv("TILESTITCH_COLORMAP_INVERT", "true")
    cfg = colormap_config_from_env()
    assert cfg.invert is True


def test_env_invert_false(monkeypatch):
    monkeypatch.setenv("TILESTITCH_COLORMAP_INVERT", "false")
    cfg = colormap_config_from_env()
    assert cfg.invert is False
