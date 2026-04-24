"""Glitch effect: randomly displaces horizontal scanlines for a digital-corruption look."""

from __future__ import annotations

import random
from dataclasses import dataclass

from PIL import Image


class GlitchError(Exception):
    """Raised when glitch configuration or processing fails."""


@dataclass
class GlitchConfig:
    """Parameters controlling the glitch effect."""

    enabled: bool = True
    intensity: float = 0.3  # fraction of rows affected (0.0–1.0)
    max_shift: int = 20     # maximum horizontal pixel shift
    seed: int | None = None  # optional RNG seed for reproducibility

    def __post_init__(self) -> None:
        if not 0.0 <= self.intensity <= 1.0:
            raise GlitchError(
                f"intensity must be between 0.0 and 1.0, got {self.intensity}"
            )
        if self.max_shift < 1:
            raise GlitchError(
                f"max_shift must be at least 1, got {self.max_shift}"
            )


def glitch_config_from_env() -> GlitchConfig:
    """Build a GlitchConfig from environment variables."""
    import os

    raw_enabled = os.getenv("TILESTITCH_GLITCH_ENABLED", "false").strip().lower()
    enabled = raw_enabled in ("1", "true", "yes")
    intensity = float(os.getenv("TILESTITCH_GLITCH_INTENSITY", "0.3"))
    max_shift = int(os.getenv("TILESTITCH_GLITCH_MAX_SHIFT", "20"))
    seed_raw = os.getenv("TILESTITCH_GLITCH_SEED", "")
    seed = int(seed_raw) if seed_raw.strip() else None
    return GlitchConfig(enabled=enabled, intensity=intensity, max_shift=max_shift, seed=seed)


def apply_glitch(image: Image.Image, config: GlitchConfig) -> Image.Image:
    """Return a copy of *image* with the glitch effect applied."""
    if not config.enabled:
        return image

    img = image.convert("RGBA")
    width, height = img.size
    pixels = img.load()

    rng = random.Random(config.seed)
    affected = max(1, int(height * config.intensity))
    rows = rng.sample(range(height), min(affected, height))

    for row in rows:
        shift = rng.randint(-config.max_shift, config.max_shift)
        if shift == 0:
            continue
        scanline = [pixels[x, row] for x in range(width)]
        for x in range(width):
            src = (x - shift) % width
            pixels[x, row] = scanline[src]

    return img
