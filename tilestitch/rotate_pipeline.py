from __future__ import annotations

from dataclasses import dataclass
from PIL import Image

from tilestitch.tile_rotate import RotateConfig, rotate_image, rotate_config_from_env


@dataclass
class RotateStage:
    config: RotateConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or self.config.angle == 0.0:
            return image
        return rotate_image(image, self.config)


def build_rotate_stage(config: RotateConfig | None = None) -> RotateStage:
    if config is None:
        config = rotate_config_from_env()
    return RotateStage(config=config)
