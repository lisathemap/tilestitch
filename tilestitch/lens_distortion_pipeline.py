"""Pipeline stage for lens distortion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_lens_distortion import (
    LensDistortionConfig,
    apply_lens_distortion,
    lens_distortion_config_from_env,
)


@dataclass
class LensDistortionStage:
    """Applies lens distortion as a pipeline stage."""

    config: Optional[LensDistortionConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_lens_distortion(image, self.config)


def build_lens_distortion_stage(
    config: Optional[LensDistortionConfig] = None,
) -> LensDistortionStage:
    """Build a LensDistortionStage, loading config from env if not provided."""
    if config is None:
        config = lens_distortion_config_from_env()
    return LensDistortionStage(config=config)
