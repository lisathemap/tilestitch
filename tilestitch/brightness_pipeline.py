"""Pipeline stage that applies brightness/contrast adjustment."""
from __future__ import annotations

from dataclasses import dataclass
from PIL import Image

from tilestitch.tile_brightness import BrightnessConfig, adjust_brightness


@dataclass
class BrightnessStage:
    config: BrightnessConfig | None
    enabled: bool = True

    def process(self, image: Image.Image) -> Image.Image:
        if not self.enabled or self.config is None:
            return image
        return adjust_brightness(image, self.config)


def build_brightness_stage(
    config: BrightnessConfig | None = None,
    enabled: bool = True,
) -> BrightnessStage:
    return BrightnessStage(config=config, enabled=enabled)
