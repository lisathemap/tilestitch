from __future__ import annotations

from dataclasses import dataclass
from PIL import Image
from typing import Optional

from tilestitch.tile_denoise import DenoiseConfig, apply_denoise, denoise_config_from_env


@dataclass
class DenoiseStage:
    config: Optional[DenoiseConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None:
            return image
        if not self.config.enabled:
            return image
        return apply_denoise(image, self.config)


def build_denoise_stage(config: Optional[DenoiseConfig] = None) -> DenoiseStage:
    if config is None:
        config = denoise_config_from_env()
    return DenoiseStage(config=config)
