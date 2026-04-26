"""Pipeline stage for chromatic aberration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_chromatic_aberration import (
    ChromaticAberrationConfig,
    apply_chromatic_aberration,
)


@dataclass
class ChromaticAberrationStage:
    """Wraps chromatic aberration as a pipeline stage."""

    config: Optional[ChromaticAberrationConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_chromatic_aberration(image, self.config)


def build_chromatic_aberration_stage(
    config: Optional[ChromaticAberrationConfig] = None,
) -> ChromaticAberrationStage:
    """Construct a ChromaticAberrationStage, defaulting to a new config."""
    if config is None:
        config = ChromaticAberrationConfig()
    return ChromaticAberrationStage(config=config)
