from __future__ import annotations

from dataclasses import dataclass
from PIL import Image

from tilestitch.tile_colorize import ColorizeConfig, apply_colorize


@dataclass
class ColorizeStage:
    config: ColorizeConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_colorize(image, self.config)


def build_colorize_stage(config: ColorizeConfig | None = None) -> ColorizeStage:
    return ColorizeStage(config=config)
