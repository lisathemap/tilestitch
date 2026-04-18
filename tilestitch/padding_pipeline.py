from __future__ import annotations

from dataclasses import dataclass
from PIL import Image

from tilestitch.tile_padding import PaddingConfig, apply_padding


@dataclass
class PaddingStage:
    config: PaddingConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        if self.config is None or not self.config.any_set:
            return image
        return apply_padding(image, self.config)


def build_padding_stage(config: PaddingConfig | None = None) -> PaddingStage:
    """Return a PaddingStage, defaulting to env-derived config if none given."""
    from tilestitch.tile_padding import padding_config_from_env
    if config is None:
        config = padding_config_from_env()
    return PaddingStage(config=config)
