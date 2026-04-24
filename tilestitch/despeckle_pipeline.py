"""Pipeline stage that applies despeckle filtering to the stitched image."""

from __future__ import annotations

from dataclasses import dataclass
from PIL import Image

from tilestitch.tile_despeckle import DespeckleConfig, apply_despeckle


@dataclass
class DespeckleStage:
    """Wraps :func:`apply_despeckle` as a reusable pipeline stage."""

    config: DespeckleConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        """Return the despeckled image, or *image* unchanged if disabled."""
        if self.config is None:
            return image
        if not self.config.enabled:
            return image
        return apply_despeckle(image, self.config)


def build_despeckle_stage(
    config: DespeckleConfig | None = None,
) -> DespeckleStage:
    """Construct a :class:`DespeckleStage` from *config*.

    If *config* is ``None`` a default :class:`DespeckleConfig` is used.
    """
    if config is None:
        config = DespeckleConfig()
    return DespeckleStage(config=config)
