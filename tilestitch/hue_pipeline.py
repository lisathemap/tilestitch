from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_hue import HueConfig, apply_hue


@dataclass
class HueStage:
    config: Optional[HueConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None:
            return image
        return apply_hue(image, self.config)


def build_hue_stage(config: Optional[HueConfig] = None) -> HueStage:
    """Return a :class:`HueStage` using *config*, or defaults from the environment."""
    if config is None:
        config = HueConfig()
    return HueStage(config=config)
