from __future__ import annotations

from dataclasses import dataclass
from PIL import Image

from tilestitch.tile_pixelate import PixelateConfig, apply_pixelate


@dataclass
class PixelateStage:
    config: PixelateConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_pixelate(image, self.config)


def build_pixelate_stage(config: PixelateConfig | None = None) -> PixelateStage:
    return PixelateStage(config=config)
