"""Pipeline stage for the halftone effect."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_halftone import HalftoneConfig, apply_halftone


@dataclass
class HalftoneStage:
    """Applies a halftone effect as a pipeline stage."""

    config: Optional[HalftoneConfig]

    def process(self, image: Image.Image) -> Image.Image:
        """Return *image* with the halftone effect applied (if enabled)."""
        if self.config is None:
            return image
        if not self.config.enabled:
            return image
        return apply_halftone(image, self.config)


def build_halftone_stage(config: Optional[HalftoneConfig] = None) -> HalftoneStage:
    """Construct a :class:`HalftoneStage` from *config*.

    If *config* is ``None`` a disabled stage is returned.
    """
    if config is None:
        return HalftoneStage(config=None)
    return HalftoneStage(config=config)
