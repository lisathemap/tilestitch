from __future__ import annotations

from dataclasses import dataclass
from PIL import Image

from tilestitch.tile_contrast import ContrastConfig, adjust_contrast


@dataclass
class ContrastStage:
    config: ContrastConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return adjust_contrast(image, self.config)


def build_contrast_stage(config: ContrastConfig | None = None) -> ContrastStage:
    if config is None:
        config = ContrastConfig()
    return ContrastStage(config=config)
