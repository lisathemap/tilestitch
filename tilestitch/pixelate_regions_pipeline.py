"""Pipeline stage for selective region pixelation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_pixelate_regions import (
    PixelateRegionsConfig,
    apply_pixelate_regions,
)


@dataclass
class PixelateRegionsStage:
    config: Optional[PixelateRegionsConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None:
            return image
        if not self.config.enabled:
            return image
        if not self.config.regions:
            return image
        return apply_pixelate_regions(image, self.config)


def build_pixelate_regions_stage(
    config: Optional[PixelateRegionsConfig] = None,
) -> PixelateRegionsStage:
    """Return a PixelateRegionsStage, using *config* or a default instance."""
    if config is None:
        from tilestitch.tile_pixelate_regions import pixelate_regions_config_from_env

        config = pixelate_regions_config_from_env()
    return PixelateRegionsStage(config=config)
