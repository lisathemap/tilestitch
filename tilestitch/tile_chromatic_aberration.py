"""Chromatic aberration effect for map tiles."""
from __future__ import annotations

from dataclasses import dataclass
import os

from PIL import Image


class ChromaticAberrationError(Exception):
    """Raised when chromatic aberration configuration is invalid."""


@dataclass
class ChromaticAberrationConfig:
    """Configuration for the chromatic aberration effect."""

    shift: int = 3
    enabled: bool = True

    def __post_init__(self) -> None:
        if self.shift < 0:
            raise ChromaticAberrationError("shift must be >= 0")
        if self.shift > 50:
            raise ChromaticAberrationError("shift must be <= 50")


def chromatic_aberration_config_from_env() -> ChromaticAberrationConfig:
    """Build a ChromaticAberrationConfig from environment variables."""
    raw_shift = os.environ.get("TILESTITCH_CA_SHIFT", "3")
    raw_enabled = os.environ.get("TILESTITCH_CA_ENABLED", "true")
    try:
        shift = int(raw_shift)
    except ValueError as exc:
        raise ChromaticAberrationError(f"invalid CA shift: {raw_shift!r}") from exc
    enabled = raw_enabled.strip().lower() not in ("0", "false", "no", "off")
    return ChromaticAberrationConfig(shift=shift, enabled=enabled)


def apply_chromatic_aberration(
    image: Image.Image, config: ChromaticAberrationConfig
) -> Image.Image:
    """Apply a simple RGB channel-shift chromatic aberration effect.

    The red channel is shifted left and the blue channel is shifted right
    by *config.shift* pixels.  The green channel is left in place.
    """
    if not config.enabled or config.shift == 0:
        return image

    rgba = image.convert("RGBA")
    r, g, b, a = rgba.split()
    s = config.shift
    w, h = image.size

    # Shift red channel to the left
    r_shifted = Image.new("L", (w, h), 0)
    r_shifted.paste(r.crop((s, 0, w, h)), (0, 0))

    # Shift blue channel to the right
    b_shifted = Image.new("L", (w, h), 0)
    b_shifted.paste(b.crop((0, 0, w - s, h)), (s, 0))

    result = Image.merge("RGBA", (r_shifted, g, b_shifted, a))
    return result.convert(image.mode)
