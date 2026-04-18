"""Pipeline stage for vignette effect."""
from __future__ import annotations

from dataclasses import dataclass
from PIL import Image

from tilestitch.tile_vignette import VignetteConfig, apply_vignette


@dataclass
class VignetteStage:
    config: VignetteConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_vignette(image, self.config)


def build_vignette_stage(config: VignetteConfig | None = None) -> VignetteStage:
    """Return a VignetteStage, loading from env when *config* is None."""
    if config is None:
        from tilestitch.tile_vignette import vignette_config_from_env
        config = vignette_config_from_env()
    return VignetteStage(config=config)
