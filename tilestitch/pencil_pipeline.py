from __future__ import annotations

from PIL import Image

from tilestitch.tile_pencil import PencilConfig, apply_pencil


class PencilStage:
    """Pipeline stage that applies a pencil-sketch effect to an image."""

    def __init__(self, config: PencilConfig | None = None) -> None:
        self._config = config

    def process(self, image: Image.Image) -> Image.Image:
        if self._config is None or not self._config.enabled:
            return image
        return apply_pencil(image, self._config)


def build_pencil_stage(config: PencilConfig | None = None) -> PencilStage:
    """Construct a PencilStage from an optional config."""
    return PencilStage(config=config)
