"""Pipeline stage for the sketch effect."""
from __future__ import annotations

from dataclasses import dataclass
from PIL import Image

from tilestitch.tile_sketch import SketchConfig, apply_sketch


@dataclass
class SketchStage:
    config: SketchConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_sketch(image, self.config)


def build_sketch_stage(config: SketchConfig | None = None) -> SketchStage:
    """Return a SketchStage, falling back to env-based config when None."""
    from tilestitch.tile_sketch import sketch_config_from_env

    if config is None:
        config = sketch_config_from_env()
    return SketchStage(config=config)
