"""Apply a colour tint to an image."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from PIL import Image, ImageChops


class TintError(ValueError):
    pass


def _parse_colour(value: str) -> Tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise TintError(f"Colour must be a 6-digit hex string, got: {value!r}")
    try:
        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)
    except ValueError:
        raise TintError(f"Invalid hex colour: {value!r}")
    return r, g, b


@dataclass
class TintConfig:
    colour: str = "ff0000"
    strength: float = 0.3
    enabled: bool = True

    def __post_init__(self) -> None:
        _parse_colour(self.colour)  # validate early
        if not 0.0 < self.strength <= 1.0:
            raise TintError("strength must be in range (0, 1]")

    @property
    def rgb(self) -> Tuple[int, int, int]:
        return _parse_colour(self.colour)


def tint_config_from_env() -> TintConfig:
    import os
    return TintConfig(
        colour=os.environ.get("TILESTITCH_TINT_COLOUR", "ff0000"),
        strength=float(os.environ.get("TILESTITCH_TINT_STRENGTH", "0.3")),
        enabled=os.environ.get("TILESTITCH_TINT_ENABLED", "false").lower() == "true",
    )


def apply_tint(image: Image.Image, config: TintConfig) -> Image.Image:
    """Blend a solid colour over *image* at the configured strength."""
    if not config.enabled:
        return image
    base = image.convert("RGBA")
    r, g, b = config.rgb
    alpha = int(config.strength * 255)
    overlay = Image.new("RGBA", base.size, (r, g, b, alpha))
    tinted = Image.alpha_composite(base, overlay)
    if image.mode != "RGBA":
        tinted = tinted.convert(image.mode)
    return tinted
