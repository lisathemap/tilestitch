from __future__ import annotations

from dataclasses import dataclass
from PIL import Image
import os


class SepiaError(Exception):
    """Raised when sepia conversion fails."""


@dataclass
class SepiaConfig:
    enabled: bool = True
    intensity: float = 1.0  # 0.0 = no effect, 1.0 = full sepia

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise SepiaError("enabled must be a bool")
        if not (0.0 <= self.intensity <= 1.0):
            raise SepiaError("intensity must be between 0.0 and 1.0")


def sepia_config_from_env() -> SepiaConfig:
    enabled = os.environ.get("TILESTITCH_SEPIA_ENABLED", "false").lower() == "true"
    intensity = float(os.environ.get("TILESTITCH_SEPIA_INTENSITY", "1.0"))
    return SepiaConfig(enabled=enabled, intensity=intensity)


def apply_sepia(image: Image.Image, config: SepiaConfig) -> Image.Image:
    """Apply a sepia tone effect to an image."""
    if not config.enabled:
        return image

    src = image.convert("RGBA")
    r_data, g_data, b_data, a_data = src.split()

    r_px = list(r_data.getdata())
    g_px = list(g_data.getdata())
    b_px = list(b_data.getdata())

    new_r, new_g, new_b = [], [], []
    t = config.intensity

    for r, g, b in zip(r_px, g_px, b_px):
        sr = min(255, int(r * 0.393 + g * 0.769 + b * 0.189))
        sg = min(255, int(r * 0.349 + g * 0.686 + b * 0.168))
        sb = min(255, int(r * 0.272 + g * 0.534 + b * 0.131))
        new_r.append(int(r + (sr - r) * t))
        new_g.append(int(g + (sg - g) * t))
        new_b.append(int(b + (sb - b) * t))

    out = Image.new("RGBA", src.size)
    pixels = list(zip(new_r, new_g, new_b, list(a_data.getdata())))
    out.putdata(pixels)
    return out
