from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_emboss import EmbossConfig, apply_emboss, emboss_config_from_env


@dataclass
class EmbossStage:
    config: Optional[EmbossConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_emboss(image, self.config)


def build_emboss_stage(config: Optional[EmbossConfig] = None) -> EmbossStage:
    """Build an EmbossStage, reading config from env if not provided."""
    if config is None:
        config = emboss_config_from_env()
    return EmbossStage(config=config)
