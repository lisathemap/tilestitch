from __future__ import annotations

from dataclasses import dataclass
from PIL import Image, ImageFilter
import os


class DenoiseError(Exception):
    pass


@dataclass
class DenoiseConfig:
    enabled: bool = True
    iterations: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise DenoiseError("enabled must be a bool")
        if self.iterations < 1:
            raise DenoiseError("iterations must be at least 1")
        if self.iterations > 10:
            raise DenoiseError("iterations must not exceed 10")


def denoise_config_from_env() -> DenoiseConfig:
    enabled = os.environ.get("TILESTITCH_DENOISE_ENABLED", "true").strip().lower() != "false"
    iterations = int(os.environ.get("TILESTITCH_DENOISE_ITERATIONS", "1"))
    return DenoiseConfig(enabled=enabled, iterations=iterations)


def apply_denoise(image: Image.Image, config: DenoiseConfig) -> Image.Image:
    """Apply median filter iteratively to reduce noise."""
    if not config.enabled:
        return image
    result = image.convert("RGBA")
    for _ in range(config.iterations):
        result = result.filter(ImageFilter.MedianFilter(size=3))
    if image.mode != "RGBA":
        result = result.convert(image.mode)
    return result
