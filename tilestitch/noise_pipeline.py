"""Pipeline stage that applies noise reduction to the stitched image."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_noise import NoiseConfig, apply_noise_reduction, noise_config_from_env


@dataclass
class NoiseStage:
    config: Optional[NoiseConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_noise_reduction(image, self.config)


def build_noise_stage(config: Optional[NoiseConfig] = None) -> NoiseStage:
    """Return a :class:`NoiseStage`, loading config from env when *config* is None."""
    if config is None:
        config = noise_config_from_env()
    return NoiseStage(config=config)
