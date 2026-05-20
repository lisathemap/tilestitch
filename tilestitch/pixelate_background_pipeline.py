"""Pipeline stage for background pixelation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_pixelate_background import (
    PixelateBackgroundConfig,
    apply_pixelate_background,
    pixelate_background_config_from_env,
)


@dataclass
class PixelateBackgroundStage:
    config: Optional[PixelateBackgroundConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None:
            return image
        if not self.config.enabled:
            return image
        return apply_pixelate_background(image, self.config)


def build_pixelate_background_stage(
    config: Optional[PixelateBackgroundConfig] = None,
) -> PixelateBackgroundStage:
    if config is None:
        config = pixelate_background_config_from_env()
    return PixelateBackgroundStage(config=config)
