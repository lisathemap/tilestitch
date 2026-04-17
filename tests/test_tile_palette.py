"""Tests for tilestitch.tile_palette and tilestitch.palette_config."""
import pytest

from tilestitch.tile_palette import (
    PaletteError,
    TilePalette,
    _validate_colour,
    get_palette,
    list_palettes,
    register_palette,
)
from tilestitch.palette_config import PaletteConfig, palette_config_from_env


# ---------------------------------------------------------------------------
# TilePalette construction
# ---------------------------------------------------------------------------

class TestTilePalette:
    def test_valid_palette_stores_name(self):
        p = TilePalette("test")
        assert p.name == "test"

    def test_empty_name_raises(self):
        with pytest.raises(PaletteError):
            TilePalette("")

    def test_whitespace_name_raises(self):
        with pytest.raises(PaletteError):
            TilePalette("   ")

    def test_colours_stored(self):
        p = TilePalette("rgb", [(255, 0, 0), (0, 255, 0)])
        assert len(p) == 2

    def test_invalid_colour_in_init_raises(self):
        with pytest.raises(PaletteError):
            TilePalette("bad", [(300, 0, 0)])

    def test_add_colour(self):
        p = TilePalette("x")
        p.add((10, 20, 30))
        assert len(p) == 1

    def test_add_invalid_colour_raises(self):
        p = TilePalette("x")
        with pytest.raises(PaletteError):
            p.add((10, 20))


# ---------------------------------------------------------------------------
# _validate_colour
# ---------------------------------------------------------------------------

def test_validate_colour_ok():
    _validate_colour((0, 128, 255))  # should not raise

def test_validate_colour_wrong_length():
    with pytest.raises(PaletteError):
        _validate_colour((1, 2))

def test_validate_colour_out_of_range():
    with pytest.raises(PaletteError):
        _validate_colour((0, 0, 256))

def test_validate_colour_negative():
    with pytest.raises(PaletteError):
        _validate_colour((-1, 0, 0))


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------

def test_list_palettes_contains_greyscale():
    assert "greyscale" in list_palettes()

def test_list_palettes_contains_viridis():
    assert "viridis" in list_palettes()

def test_get_palette_returns_tile_palette():
    p = get_palette("greyscale")
    assert isinstance(p, TilePalette)

def test_get_palette_case_insensitive():
    p = get_palette("GREYSCALE")
    assert p.name == "greyscale"

def test_get_unknown_palette_raises():
    with pytest.raises(PaletteError):
        get_palette("nonexistent_palette_xyz")

def test_register_palette_then_get():
    custom = TilePalette("custom_test", [(1, 2, 3)])
    register_palette(custom)
    assert get_palette("custom_test") is custom


# ---------------------------------------------------------------------------
# PaletteConfig
# ---------------------------------------------------------------------------

class TestPaletteConfig:
    def test_defaults(self):
        cfg = PaletteConfig()
        assert cfg.palette_name == "greyscale"
        assert cfg.apply_to_output is False

    def test_valid_name_accepted(self):
        cfg = PaletteConfig(palette_name="viridis")
        assert cfg.palette_name == "viridis"

    def test_invalid_name_raises(self):
        with pytest.raises(PaletteError):
            PaletteConfig(palette_name="does_not_exist")

    def test_from_env_defaults(self, monkeypatch):
        monkeypatch.delenv("TILESTITCH_PALETTE", raising=False)
        monkeypatch.delenv("TILESTITCH_PALETTE_APPLY", raising=False)
        cfg = palette_config_from_env()
        assert cfg.palette_name == "greyscale"
        assert cfg.apply_to_output is False

    def test_from_env_custom(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_PALETTE", "viridis")
        monkeypatch.setenv("TILESTITCH_PALETTE_APPLY", "true")
        cfg = palette_config_from_env()
        assert cfg.palette_name == "viridis"
        assert cfg.apply_to_output is True
