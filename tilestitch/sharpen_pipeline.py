"""Pipeline stage that applies sharpening to the stitched image."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_sharpen import SharpenConfig, apply_sharpen, sharpen_config_from_env


@dataclass
class SharpenStage:
    config: Optional[SharpenConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_sharpen(image, self.config)


def build_sharpen_stage(config: Optional[SharpenConfig] = None) -> SharpenStage:
    if config is None:
        config = sharpen_config_from_env()
    return SharpenStage(config=config)
