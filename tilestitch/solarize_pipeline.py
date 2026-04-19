"""Pipeline stage that applies solarize to the stitched image."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_solarize import SolarizeConfig, apply_solarize, solarize_config_from_env


@dataclass
class SolarizeStage:
    config: Optional[SolarizeConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_solarize(image, self.config)


def build_solarize_stage(config: Optional[SolarizeConfig] = None) -> SolarizeStage:
    """Return a SolarizeStage, loading config from env when not provided."""
    if config is None:
        config = solarize_config_from_env()
    return SolarizeStage(config=config)
