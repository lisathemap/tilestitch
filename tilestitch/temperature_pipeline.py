"""Pipeline stage that applies colour temperature adjustment."""
from __future__ import annotations

from typing import Optional

from PIL import Image

from tilestitch.tile_temperature import TemperatureConfig, apply_temperature


class TemperatureStage:
    """Applies colour temperature adjustment as a pipeline stage."""

    def __init__(self, config: Optional[TemperatureConfig]) -> None:
        self._config = config

    def process(self, image: Image.Image) -> Image.Image:
        if self._config is None or not self._config.enabled:
            return image
        return apply_temperature(image, self._config)


def build_temperature_stage(
    config: Optional[TemperatureConfig] = None,
) -> TemperatureStage:
    """Construct a :class:`TemperatureStage`, defaulting to env-based config."""
    if config is None:
        from tilestitch.tile_temperature import temperature_config_from_env

        config = temperature_config_from_env()
    return TemperatureStage(config)
