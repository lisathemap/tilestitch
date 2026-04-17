"""Pipeline stage that optionally applies a colour map to the stitched image."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_colormap import ColormapConfig, apply_colormap


@dataclass
class ColormapStage:
    config: Optional[ColormapConfig]
    enabled: bool = True

    def process(self, image: Image.Image) -> Image.Image:
        """Apply colour map if enabled and config is present."""
        if not self.enabled or self.config is None:
            return image
        return apply_colormap(image, self.config)


def build_colormap_stage(
    enabled: bool = False,
    config: Optional[ColormapConfig] = None,
) -> ColormapStage:
    """Construct a ColormapStage with sensible defaults."""
    if enabled and config is None:
        config = ColormapConfig()
    return ColormapStage(config=config, enabled=enabled)
