"""Pipeline stage that applies the threshold filter."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_threshold import ThresholdConfig, apply_threshold


@dataclass
class ThresholdStage:
    config: Optional[ThresholdConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_threshold(image, self.config)


def build_threshold_stage(config: Optional[ThresholdConfig] = None) -> ThresholdStage:
    """Return a ThresholdStage, creating a default config when none is given."""
    if config is None:
        config = ThresholdConfig()
    return ThresholdStage(config=config)
