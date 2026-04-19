"""Pipeline stage that applies an overlay to the stitched image."""
from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from tilestitch.tile_overlay import OverlayConfig, apply_overlay


@dataclass
class OverlayStage:
    config: OverlayConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_overlay(image, self.config)


def build_overlay_stage(config: OverlayConfig | None = None) -> OverlayStage:
    """Construct an OverlayStage, optionally reading config from the environment."""
    if config is None:
        from tilestitch.tile_overlay import overlay_config_from_env
        config = overlay_config_from_env()
    return OverlayStage(config=config)
