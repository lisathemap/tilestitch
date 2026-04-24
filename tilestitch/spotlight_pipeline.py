"""Pipeline stage that applies the spotlight effect."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_spotlight import SpotlightConfig, apply_spotlight


@dataclass
class SpotlightStage:
    config: Optional[SpotlightConfig]

    def process(self, image: Image.Image) -> Image.Image:
        """Return the image with spotlight applied, or unchanged if disabled."""
        if self.config is None:
            return image
        if not self.config.enabled:
            return image
        return apply_spotlight(image, self.config)


def build_spotlight_stage(
    config: Optional[SpotlightConfig] = None,
) -> SpotlightStage:
    """Construct a SpotlightStage, falling back to env-derived config."""
    if config is None:
        from tilestitch.tile_spotlight import spotlight_config_from_env
        config = spotlight_config_from_env()
    return SpotlightStage(config=config)
