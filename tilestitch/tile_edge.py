"""Edge detection filter for stitched tile images."""
from __future__ import annotations

from dataclasses import dataclass
from PIL import Image, ImageFilter


class EdgeError(Exception):
    """Raised when edge detection configuration or processing fails."""


@dataclass
class EdgeConfig:
    enabled: bool = False
    mode: str = "find"  # "find" | "enhance"

    def __post_init__(self) -> None:
        valid = {"find", "enhance"}
        if self.mode not in valid:
            raise EdgeError(f"mode must be one of {valid}, got {self.mode!r}")


def edge_config_from_env() -> EdgeConfig:
    import os

    enabled = os.environ.get("TILESTITCH_EDGE_ENABLED", "false").strip().lower() == "true"
    mode = os.environ.get("TILESTITCH_EDGE_MODE", "find").strip().lower()
    return EdgeConfig(enabled=enabled, mode=mode)


def apply_edge(image: Image.Image, config: EdgeConfig) -> Image.Image:
    """Apply edge detection to *image* according to *config*.

    The image is converted to RGBA before filtering so that transparency is
    preserved, then the filter is applied to the RGB channels only.
    """
    if not config.enabled:
        return image

    original_mode = image.mode
    rgba = image.convert("RGBA")
    rgb = rgba.convert("RGB")

    if config.mode == "find":
        filtered = rgb.filter(ImageFilter.FIND_EDGES)
    else:
        filtered = rgb.filter(ImageFilter.EDGE_ENHANCE)

    filtered_rgba = filtered.convert("RGBA")
    # Restore original alpha channel
    r, g, b, _ = filtered_rgba.split()
    _, _, _, a = rgba.split()
    result = Image.merge("RGBA", (r, g, b, a))

    if original_mode != "RGBA":
        return result.convert(original_mode)
    return result
