"""Pipeline stage that applies the pixel shift effect."""
from __future__ import annotations

from PIL import Image

from tilestitch.tile_pixelshift import PixelShiftConfig, apply_pixelshift


class PixelShiftStage:
    """Wraps pixel shift as a pipeline stage."""

    def __init__(self, config: PixelShiftConfig | None) -> None:
        self._config = config

    def process(self, image: Image.Image) -> Image.Image:
        """Return the image with pixel shift applied, or unchanged."""
        if self._config is None:
            return image
        if not self._config.enabled:
            return image
        return apply_pixelshift(image, self._config)


def build_pixelshift_stage(config: PixelShiftConfig | None = None) -> PixelShiftStage:
    """Construct a PixelShiftStage, optionally loading config from env."""
    if config is None:
        from tilestitch.tile_pixelshift import pixelshift_config_from_env

        try:
            config = pixelshift_config_from_env()
        except Exception:
            return PixelShiftStage(None)
    return PixelShiftStage(config)
