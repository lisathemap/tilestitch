from __future__ import annotations

import os
from dataclasses import dataclass
from PIL import Image, ImageDraw


class CrosshatchError(Exception):
    """Raised when crosshatch configuration or application fails."""


@dataclass
class CrosshatchConfig:
    enabled: bool = True
    spacing: int = 16
    line_width: int = 1
    colour: str = "#000000"
    opacity: float = 0.3

    def __post_init__(self) -> None:
        if self.spacing < 2:
            raise CrosshatchError("spacing must be at least 2")
        if self.line_width < 1:
            raise CrosshatchError("line_width must be at least 1")
        if not (0.0 <= self.opacity <= 1.0):
            raise CrosshatchError("opacity must be between 0.0 and 1.0")
        try:
            _parse_colour(self.colour)
        except ValueError as exc:
            raise CrosshatchError(f"invalid colour: {exc}") from exc


def _parse_colour(hex_colour: str) -> tuple[int, int, int]:
    h = hex_colour.strip().lstrip("#")
    if len(h) != 6:
        raise ValueError(f"expected 6-digit hex colour, got {hex_colour!r}")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def crosshatch_config_from_env() -> CrosshatchConfig:
    """Build a CrosshatchConfig from environment variables."""
    raw_enabled = os.environ.get("TILESTITCH_CROSSHATCH_ENABLED", "true")
    enabled = raw_enabled.strip().lower() not in ("false", "0", "no")
    spacing = int(os.environ.get("TILESTITCH_CROSSHATCH_SPACING", "16"))
    line_width = int(os.environ.get("TILESTITCH_CROSSHATCH_LINE_WIDTH", "1"))
    colour = os.environ.get("TILESTITCH_CROSSHATCH_COLOUR", "#000000")
    opacity = float(os.environ.get("TILESTITCH_CROSSHATCH_OPACITY", "0.3"))
    return CrosshatchConfig(
        enabled=enabled,
        spacing=spacing,
        line_width=line_width,
        colour=colour,
        opacity=opacity,
    )


def apply_crosshatch(image: Image.Image, config: CrosshatchConfig) -> Image.Image:
    """Overlay a crosshatch pattern on *image* and return the result."""
    if not config.enabled:
        return image

    base = image.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    r, g, b = _parse_colour(config.colour)
    alpha = int(config.opacity * 255)
    line_colour = (r, g, b, alpha)

    width, height = base.size
    for x in range(0, width, config.spacing):
        draw.line([(x, 0), (x, height)], fill=line_colour, width=config.line_width)
    for y in range(0, height, config.spacing):
        draw.line([(0, y), (width, y)], fill=line_colour, width=config.line_width)

    result = Image.alpha_composite(base, overlay)
    if image.mode != "RGBA":
        result = result.convert(image.mode)
    return result
