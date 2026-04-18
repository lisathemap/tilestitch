from __future__ import annotations

from PIL import Image

from tilestitch.tile_grayscale import GrayscaleConfig, convert_to_grayscale


class GrayscaleStage:
    """Pipeline stage that optionally converts an image to grayscale."""

    def __init__(self, config: GrayscaleConfig | None) -> None:
        self._config = config

    def process(self, image: Image.Image) -> Image.Image:
        if self._config is None:
            return image
        if not self._config.enabled:
            return image
        return convert_to_grayscale(image, self._config)


def build_grayscale_stage(config: GrayscaleConfig | None = None) -> GrayscaleStage:
    """Construct a GrayscaleStage from an optional config.

    If *config* is None a no-op stage is returned.
    """
    return GrayscaleStage(config)
