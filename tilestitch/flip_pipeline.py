"""Pipeline stage that applies optional image flipping."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_flipper import FlipConfig, flip_image


@dataclass
class FlipStage:
    config: Optional[FlipConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return flip_image(image, self.config)


def build_flip_stage(config: Optional[FlipConfig] = None) -> FlipStage:
    """Construct a :class:`FlipStage`, falling back to env-based config."""
    if config is None:
        from tilestitch.tile_flipper import flip_config_from_env
        config = flip_config_from_env()
    return FlipStage(config=config)
