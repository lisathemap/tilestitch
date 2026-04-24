"""Hillshade / relief-shading filter for stitched tile images."""
from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
from PIL import Image


class ReliefError(Exception):
    """Raised when relief configuration or processing fails."""


@dataclass
class ReliefConfig:
    """Configuration for the hillshade relief effect."""

    enabled: bool = True
    azimuth: float = 315.0   # degrees, light source direction
    altitude: float = 45.0   # degrees, light source elevation
    z_factor: float = 1.0    # vertical exaggeration
    blend: float = 0.6       # 0.0 = original, 1.0 = full relief

    def __post_init__(self) -> None:
        if not 0.0 <= self.azimuth < 360.0:
            raise ReliefError("azimuth must be in [0, 360)")
        if not 0.0 < self.altitude <= 90.0:
            raise ReliefError("altitude must be in (0, 90]")
        if self.z_factor <= 0.0:
            raise ReliefError("z_factor must be positive")
        if not 0.0 <= self.blend <= 1.0:
            raise ReliefError("blend must be in [0.0, 1.0]")


def relief_config_from_env() -> ReliefConfig:
    """Build a ReliefConfig from environment variables."""
    return ReliefConfig(
        enabled=os.environ.get("TILESTITCH_RELIEF_ENABLED", "true").lower() == "true",
        azimuth=float(os.environ.get("TILESTITCH_RELIEF_AZIMUTH", "315")),
        altitude=float(os.environ.get("TILESTITCH_RELIEF_ALTITUDE", "45")),
        z_factor=float(os.environ.get("TILESTITCH_RELIEF_Z_FACTOR", "1.0")),
        blend=float(os.environ.get("TILESTITCH_RELIEF_BLEND", "0.6")),
    )


def apply_relief(image: Image.Image, config: ReliefConfig) -> Image.Image:
    """Apply a hillshade relief effect to *image* and return the result."""
    if not config.enabled:
        return image

    # Work on a luminance representation of the image.
    original = image.convert("RGBA")
    grey = np.asarray(image.convert("L"), dtype=np.float64)

    # Compute surface normals via Sobel-like gradients.
    dz_dx = np.gradient(grey, axis=1) * config.z_factor
    dz_dy = np.gradient(grey, axis=0) * config.z_factor

    # Convert azimuth / altitude to a light-direction vector.
    az_rad = np.radians(360.0 - config.azimuth + 90.0)
    alt_rad = np.radians(config.altitude)

    lx = np.cos(alt_rad) * np.cos(az_rad)
    ly = np.cos(alt_rad) * np.sin(az_rad)
    lz = np.sin(alt_rad)

    # Hillshade = dot(normal, light_direction), clamped to [0, 1].
    norm = np.sqrt(dz_dx**2 + dz_dy**2 + 1.0)
    shade = ((-dz_dx * lx + -dz_dy * ly + lz) / norm).clip(0.0, 1.0)

    shade_img = Image.fromarray((shade * 255).astype(np.uint8), mode="L").convert("RGBA")

    blended = Image.blend(original, shade_img, alpha=config.blend)
    return blended if image.mode == "RGBA" else blended.convert(image.mode)
