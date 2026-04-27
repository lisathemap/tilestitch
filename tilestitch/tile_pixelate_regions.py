"""Selective region pixelation — blur specific rectangular areas of a tile."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from PIL import Image


class PixelateRegionsError(Exception):
    """Raised when region pixelation configuration is invalid."""


Region = Tuple[int, int, int, int]  # (x0, y0, x1, y1) in pixels


@dataclass
class PixelateRegionsConfig:
    regions: List[Region] = field(default_factory=list)
    block_size: int = 16
    enabled: bool = True

    def __post_init__(self) -> None:
        if self.block_size < 1:
            raise PixelateRegionsError(
                f"block_size must be >= 1, got {self.block_size}"
            )
        for r in self.regions:
            if len(r) != 4:
                raise PixelateRegionsError(
                    f"Each region must be a 4-tuple (x0, y0, x1, y1), got {r!r}"
                )
            x0, y0, x1, y1 = r
            if x0 >= x1 or y0 >= y1:
                raise PixelateRegionsError(
                    f"Region {r!r} is degenerate: x0 < x1 and y0 < y1 required"
                )


def apply_pixelate_regions(
    image: Image.Image, config: PixelateRegionsConfig
) -> Image.Image:
    """Return a copy of *image* with each configured region pixelated."""
    if not config.enabled or not config.regions:
        return image

    result = image.copy().convert("RGBA")
    for region in config.regions:
        x0, y0, x1, y1 = region
        # Clamp to image bounds
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(result.width, x1)
        y1 = min(result.height, y1)
        if x0 >= x1 or y0 >= y1:
            continue
        crop = result.crop((x0, y0, x1, y1))
        w, h = crop.size
        bs = config.block_size
        small = crop.resize(
            (max(1, w // bs), max(1, h // bs)), Image.NEAREST
        )
        pixelated = small.resize((w, h), Image.NEAREST)
        result.paste(pixelated, (x0, y0))
    return result


def pixelate_regions_config_from_env() -> PixelateRegionsConfig:
    """Build a default PixelateRegionsConfig (regions supplied programmatically)."""
    import os

    block_size = int(os.environ.get("TILESTITCH_PIXELATE_REGIONS_BLOCK_SIZE", "16"))
    enabled = os.environ.get("TILESTITCH_PIXELATE_REGIONS_ENABLED", "true").lower() == "true"
    return PixelateRegionsConfig(regions=[], block_size=block_size, enabled=enabled)
