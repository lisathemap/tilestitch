"""Fog/haze overlay effect for map tiles."""
from __future__ import annotations

from dataclasses import dataclass
from PIL import Image, ImageDraw
import os


class FogError(Exception):
    """Raised when fog configuration is invalid."""


@dataclass
class FogConfig:
    """Configuration for the fog overlay effect."""

    enabled: bool = True
    density: float = 0.4
    colour: str = "#ffffff"

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise FogError("enabled must be a bool")
        if not (0.0 < self.density <= 1.0):
            raise FogError("density must be in the range (0, 1]")
        if not self.colour or not self.colour.strip():
            raise FogError("colour must not be empty")
        try:
            Image.new("RGB", (1, 1), self.colour)
        except (ValueError, TypeError) as exc:
            raise FogError(f"invalid colour: {self.colour!r}") from exc


def fog_config_from_env() -> FogConfig:
    """Build a FogConfig from environment variables."""
    enabled = os.environ.get("TILESTITCH_FOG_ENABLED", "true").lower() != "false"
    density = float(os.environ.get("TILESTITCH_FOG_DENSITY", "0.4"))
    colour = os.environ.get("TILESTITCH_FOG_COLOUR", "#ffffff")
    return FogConfig(enabled=enabled, density=density, colour=colour)


def apply_fog(image: Image.Image, config: FogConfig) -> Image.Image:
    """Overlay a semi-transparent fog layer on *image*."""
    if not config.enabled:
        return image

    base = image.convert("RGBA")
    fog_layer = Image.new("RGBA", base.size, color=config.colour)
    alpha = int(config.density * 255)
    r, g, b, _ = fog_layer.split()
    fog_layer = Image.merge("RGBA", (r, g, b, Image.new("L", base.size, alpha)))
    result = Image.alpha_composite(base, fog_layer)
    return result.convert(image.mode)
