"""Pipeline stage that applies the fog effect."""
from __future__ import annotations

from dataclasses import dataclass
from PIL import Image

from tilestitch.tile_fog import FogConfig, apply_fog, fog_config_from_env


@dataclass
class FogStage:
    """Pipeline stage wrapping :func:`apply_fog`."""

    config: FogConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        """Apply fog to *image* if the stage is active."""
        if self.config is None or not self.config.enabled:
            return image
        return apply_fog(image, self.config)


def build_fog_stage(config: FogConfig | None = None) -> FogStage:
    """Create a :class:`FogStage`, reading env vars when *config* is ``None``."""
    if config is None:
        config = fog_config_from_env()
    return FogStage(config=config)
