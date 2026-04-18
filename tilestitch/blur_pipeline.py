from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_blur import BlurConfig, apply_blur, blur_config_from_env


@dataclass
class BlurStage:
    config: Optional[BlurConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_blur(image, self.config)


def build_blur_stage(config: Optional[BlurConfig] = None) -> BlurStage:
    if config is None:
        config = blur_config_from_env()
    return BlurStage(config=config)
