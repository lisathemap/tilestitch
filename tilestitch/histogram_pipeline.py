"""Pipeline stage that applies histogram adjustment to the stitched image."""
from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from tilestitch.tile_histogram import HistogramConfig, apply_histogram


@dataclass
class HistogramStage:
    config: HistogramConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.enabled:
            return image
        return apply_histogram(image, self.config)


def build_histogram_stage(config: HistogramConfig | None = None) -> HistogramStage:
    """Return a HistogramStage, falling back to env-based config when *config* is None."""
    if config is None:
        from tilestitch.tile_histogram import histogram_config_from_env
        config = histogram_config_from_env()
    return HistogramStage(config=config)
