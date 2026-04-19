from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_saturation import SaturationConfig, apply_saturation


@dataclass
class SaturationStage:
    config: Optional[SaturationConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_saturation(image, self.config)


def build_saturation_stage(config: Optional[SaturationConfig] = None) -> SaturationStage:
    return SaturationStage(config=config)
