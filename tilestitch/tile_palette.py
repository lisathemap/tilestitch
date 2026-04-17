"""Colour palette / band-mapping helpers for exported images."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple
import os

RGBTriple = Tuple[int, int, int]


class PaletteError(ValueError):
    """Raised when a palette definition is invalid."""


@dataclass
class TilePalette:
    """A named palette that maps band indices to RGB colours."""

    name: str
    colours: List[RGBTriple] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise PaletteError("Palette name must not be empty.")
        for c in self.colours:
            _validate_colour(c)

    def add(self, colour: RGBTriple) -> None:
        _validate_colour(colour)
        self.colours.append(colour)

    def __len__(self) -> int:
        return len(self.colours)


def _validate_colour(colour: RGBTriple) -> None:
    if len(colour) != 3:
        raise PaletteError(f"Expected (R, G, B) triple, got {colour!r}.")
    for ch in colour:
        if not (0 <= ch <= 255):
            raise PaletteError(f"Channel value {ch} out of range 0-255.")


# Built-in palettes
_GREYSCALE: List[RGBTriple] = [(i, i, i) for i in range(256)]
_VIRIDIS_STOPS: List[RGBTriple] = [
    (68, 1, 84), (59, 82, 139), (33, 145, 140), (94, 201, 98), (253, 231, 37)
]

_REGISTRY: dict[str, TilePalette] = {
    "greyscale": TilePalette("greyscale", _GREYSCALE),
    "viridis": TilePalette("viridis", _VIRIDIS_STOPS),
}


def get_palette(name: str) -> TilePalette:
    key = name.strip().lower()
    if key not in _REGISTRY:
        raise PaletteError(f"Unknown palette '{name}'. Available: {list_palettes()}")
    return _REGISTRY[key]


def list_palettes() -> List[str]:
    return sorted(_REGISTRY.keys())


def register_palette(palette: TilePalette) -> None:
    _REGISTRY[palette.name.lower()] = palette


def palette_config_from_env() -> str:
    """Return palette name from TILESTITCH_PALETTE env var, defaulting to 'greyscale'."""
    return os.environ.get("TILESTITCH_PALETTE", "greyscale").strip()
