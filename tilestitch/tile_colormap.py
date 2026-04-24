"""Apply named colour maps to greyscale tile images."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import os

from PIL import Image

_BUILTIN_MAPS: dict[str, list[tuple[int, int, int]]] = {
    "viridis": [
        (68, 1, 84), (59, 82, 139), (33, 145, 140), (94, 201, 98), (253, 231, 37)
    ],
    "grayscale": [(i, i, i) for i in range(0, 256, 51)],
    "hot": [(0, 0, 0), (128, 0, 0), (255, 0, 0), (255, 128, 0), (255, 255, 255)],
}


class ColormapError(Exception):
    """Raised when a colour map operation fails."""


@dataclass
class ColormapConfig:
    name: str = "grayscale"
    invert: bool = False

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ColormapError("Colormap name must not be empty.")


def list_colormaps() -> list[str]:
    """Return names of all available built-in colour maps."""
    return list(_BUILTIN_MAPS.keys())


def _build_lut(stops: list[tuple[int, int, int]], invert: bool) -> list[int]:
    """Interpolate a 256-entry RGB LUT from colour stops."""
    lut: list[int] = []
    n = len(stops) - 1
    for i in range(256):
        t = i / 255.0
        seg = min(int(t * n), n - 1)
        local_t = t * n - seg
        r = int(stops[seg][0] + local_t * (stops[seg + 1][0] - stops[seg][0]))
        g = int(stops[seg][1] + local_t * (stops[seg + 1][1] - stops[seg][1]))
        b = int(stops[seg][2] + local_t * (stops[seg + 1][2] - stops[seg][2]))
        lut.extend([r, g, b])
    if invert:
        rgb = [lut[i:i + 3] for i in range(0, 768, 3)]
        rgb.reverse()
        lut = [v for triple in rgb for v in triple]
    return lut


def apply_colormap(image: Image.Image, config: ColormapConfig) -> Image.Image:
    """Apply a colour map to a greyscale image, returning an RGB image."""
    name = config.name.strip().lower()
    if name not in _BUILTIN_MAPS:
        raise ColormapError(f"Unknown colormap: '{name}'. Available: {list_colormaps()}")
    grey = image.convert("L")
    stops = _BUILTIN_MAPS[name]
    lut = _build_lut(stops, config.invert)
    return grey.convert("RGB").point(lut * 1)  # point on RGB needs 768-entry LUT


def colormap_config_from_env() -> ColormapConfig:
    """Build a ColormapConfig from environment variables."""
    name = os.environ.get("TILESTITCH_COLORMAP", "grayscale")
    invert = os.environ.get("TILESTITCH_COLORMAP_INVERT", "false").lower() == "true"
    try:
        return ColormapConfig(name=name, invert=invert)
    except ColormapError as exc:
        raise ColormapError(
            f"Invalid colormap configuration from environment: {exc}"
        ) from exc
