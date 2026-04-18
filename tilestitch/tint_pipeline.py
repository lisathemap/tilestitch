"""Pipeline stage for tile tinting."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_tint import TintConfig, apply_tint


@dataclass
class TintStage:
    config: Optional[TintConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_tint(image, self.config)


def build_tint_stage(config: Optional[TintConfig] = None) -> TintStage:
    return TintStage(config=config)
