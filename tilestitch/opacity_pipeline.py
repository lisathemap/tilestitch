from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_opacity import OpacityConfig, apply_opacity


@dataclass
class OpacityStage:
    config: Optional[OpacityConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_opacity(image, self.config)


def build_opacity_stage(config: Optional[OpacityConfig] = None) -> OpacityStage:
    if config is None:
        config = OpacityConfig()
    return OpacityStage(config=config)
