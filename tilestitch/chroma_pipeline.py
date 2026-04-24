"""Pipeline stage for chroma key replacement."""
from __future__ import annotations

from typing import Optional

from PIL import Image

from tilestitch.tile_chroma import ChromaConfig, apply_chroma


class ChromaStage:
    """Pipeline stage that applies chroma key replacement."""

    def __init__(self, config: Optional[ChromaConfig]) -> None:
        self._config = config

    def process(self, image: Image.Image) -> Image.Image:
        if self._config is None or not self._config.enabled:
            return image
        return apply_chroma(image, self._config)


def build_chroma_stage(config: Optional[ChromaConfig]) -> ChromaStage:
    """Construct a ChromaStage from an optional config."""
    return ChromaStage(config)
