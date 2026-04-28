"""Bloom (glow) effect for map tile images.

Applies a luminance-based bloom effect by isolating bright regions,
blurring them, and compositing the result back onto the original image.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image, ImageFilter


class BloomError(Exception):
    """Raised when bloom configuration or processing fails."""


@dataclass
class BloomConfig:
    """Configuration for the bloom (glow) effect.

    Attributes:
        enabled:   Whether the effect is active.
        threshold: Luminance threshold (0–255) above which pixels glow.
        radius:    Gaussian blur radius applied to the bright mask.
        intensity: Blend strength of the bloom layer (0.0–1.0).
    """

    enabled: bool = True
    threshold: int = 200
    radius: float = 8.0
    intensity: float = 0.5

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise BloomError("enabled must be a bool")
        if not (0 <= self.threshold <= 255):
            raise BloomError("threshold must be between 0 and 255")
        if self.radius <= 0:
            raise BloomError("radius must be greater than zero")
        if not (0.0 <= self.intensity <= 1.0):
            raise BloomError("intensity must be between 0.0 and 1.0")


def bloom_config_from_env() -> BloomConfig:
    """Build a BloomConfig from environment variables.

    Environment variables
    ---------------------
    TILESTITCH_BLOOM_ENABLED    : '1' / '0'  (default '1')
    TILESTITCH_BLOOM_THRESHOLD  : int 0-255  (default '200')
    TILESTITCH_BLOOM_RADIUS     : float > 0  (default '8.0')
    TILESTITCH_BLOOM_INTENSITY  : float 0-1  (default '0.5')
    """
    enabled = os.environ.get("TILESTITCH_BLOOM_ENABLED", "1") != "0"
    threshold = int(os.environ.get("TILESTITCH_BLOOM_THRESHOLD", "200"))
    radius = float(os.environ.get("TILESTITCH_BLOOM_RADIUS", "8.0"))
    intensity = float(os.environ.get("TILESTITCH_BLOOM_INTENSITY", "0.5"))
    return BloomConfig(
        enabled=enabled,
        threshold=threshold,
        radius=radius,
        intensity=intensity,
    )


def apply_bloom(image: Image.Image, config: BloomConfig) -> Image.Image:
    """Apply a bloom (glow) effect to *image*.

    The algorithm:
    1. Convert to RGBA to preserve transparency.
    2. Extract pixels brighter than *threshold* into a mask layer.
    3. Blur the mask with a Gaussian kernel of *radius*.
    4. Blend the blurred bright layer back onto the original using *intensity*.

    Parameters
    ----------
    image:  Source PIL image.
    config: BloomConfig controlling the effect parameters.

    Returns
    -------
    A new PIL image with bloom applied.
    """
    if not config.enabled:
        return image

    base = image.convert("RGBA")

    # Build a bright-regions mask by thresholding luminance.
    grey = base.convert("L")
    bright_mask = grey.point(lambda p: p if p >= config.threshold else 0)

    # Apply the mask to the RGBA image to isolate bright pixels.
    r, g, b, a = base.split()
    bright_r = Image.composite(r, Image.new("L", r.size, 0), bright_mask)
    bright_g = Image.composite(g, Image.new("L", g.size, 0), bright_mask)
    bright_b = Image.composite(b, Image.new("L", b.size, 0), bright_mask)
    bright_layer = Image.merge("RGBA", (bright_r, bright_g, bright_b, bright_mask))

    # Blur the bright layer to create the glow halo.
    blurred = bright_layer.filter(ImageFilter.GaussianBlur(radius=config.radius))

    # Blend the glow onto the original image.
    result = Image.blend(base, blurred, alpha=config.intensity)
    # Restore original alpha channel.
    result.putalpha(a)

    # Return in the original mode if possible.
    if image.mode != "RGBA":
        try:
            return result.convert(image.mode)
        except Exception:
            pass
    return result
