"""Mosaic effect: pixelate regions with averaged colours."""
from __future__ import annotations

from dataclasses import dataclass
from PIL import Image
import os


class MosaicError(ValueError):
    pass


@dataclass
class MosaicConfig:
    enabled: bool = True
    tile_size: int = 16

    def __post_init__(self) -> None:
        if self.tile_size < 2:
            raise MosaicError("tile_size must be >= 2")


def mosaic_config_from_env() -> MosaicConfig:
    enabled = os.environ.get("TILESTITCH_MOSAIC_ENABLED", "false").strip().lower() == "true"
    tile_size = int(os.environ.get("TILESTITCH_MOSAIC_TILE_SIZE", "16"))
    return MosaicConfig(enabled=enabled, tile_size=tile_size)


def apply_mosaic(image: Image.Image, config: MosaicConfig) -> Image.Image:
    """Apply a mosaic (large-pixel) effect to *image*."""
    if not config.enabled:
        return image
    src = image.convert("RGBA")
    w, h = src.size
    ts = config.tile_size
    out = src.copy()
    for y in range(0, h, ts):
        for x in range(0, w, ts):
            box = (x, y, min(x + ts, w), min(y + ts, h))
            region = src.crop(box)
            avg = region.resize((1, 1), Image.BILINEAR).resize(
                (box[2] - box[0], box[3] - box[1]), Image.NEAREST
            )
            out.paste(avg, (x, y))
    return out.convert(image.mode)
