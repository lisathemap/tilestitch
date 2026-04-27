"""Pipeline stage that applies relief shadow to a stitched image."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_relief_shadow import (
    ReliefShadowConfig,
    apply_relief_shadow,
    relief_shadow_config_from_env,
)


@dataclass
class ReliefShadowStage:
    config: Optional[ReliefShadowConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None:
            return image
        if not self.config.enabled:
            return image
        return apply_relief_shadow(image, self.config)


def build_relief_shadow_stage(
    config: Optional[ReliefShadowConfig] = None,
    *,
    from_env: bool = False,
) -> ReliefShadowStage:
    """Return a ReliefShadowStage, optionally built from env vars."""
    if from_env:
        config = relief_shadow_config_from_env()
    return ReliefShadowStage(config=config)
