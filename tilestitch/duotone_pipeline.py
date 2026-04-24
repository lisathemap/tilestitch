"""Pipeline stage that applies the duotone effect."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_duotone import DuotoneConfig, apply_duotone


@dataclass
class DuotoneStage:
    """Wraps :func:`apply_duotone` as a reusable pipeline stage."""

    config: Optional[DuotoneConfig]

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None:
            return image
        if not self.config.enabled:
            return image
        return apply_duotone(image, self.config)


def build_duotone_stage(
    config: Optional[DuotoneConfig] = None,
) -> DuotoneStage:
    """Construct a :class:`DuotoneStage`, defaulting to *config* from env."""
    if config is None:
        from tilestitch.tile_duotone import duotone_config_from_env

        config = duotone_config_from_env()
    return DuotoneStage(config=config)
