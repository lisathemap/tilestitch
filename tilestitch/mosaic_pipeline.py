"""Pipeline stage that applies the mosaic effect."""
from __future__ import annotations

from dataclasses import dataclass
from PIL import Image

from tilestitch.tile_mosaic import MosaicConfig, apply_mosaic, mosaic_config_from_env


@dataclass
class MosaicStage:
    config: MosaicConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_mosaic(image, self.config)


def build_mosaic_stage(config: MosaicConfig | None = None) -> MosaicStage:
    if config is None:
        config = mosaic_config_from_env()
    return MosaicStage(config=config)
