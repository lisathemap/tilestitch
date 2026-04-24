"""Pipeline stage that applies the mosaic effect."""
from __future__ import annotations

from dataclasses import dataclass
from PIL import Image

from tilestitch.tile_mosaic import MosaicConfig, apply_mosaic, mosaic_config_from_env


@dataclass
class MosaicStage:
    """Pipeline stage that conditionally applies a mosaic (pixelation) effect."""

    config: MosaicConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        """Apply the mosaic effect to *image* and return the result.

        If the stage is disabled (``config`` is ``None`` or
        ``config.enabled`` is ``False``), the original image is returned
        unchanged.
        """
        if self.config is None or not self.config.enabled:
            return image
        return apply_mosaic(image, self.config)

    @property
    def enabled(self) -> bool:
        """Return ``True`` when this stage will actively transform images."""
        return self.config is not None and self.config.enabled


def build_mosaic_stage(config: MosaicConfig | None = None) -> MosaicStage:
    """Construct a :class:`MosaicStage`, loading config from the environment
    when *config* is not provided explicitly.
    """
    if config is None:
        config = mosaic_config_from_env()
    return MosaicStage(config=config)
