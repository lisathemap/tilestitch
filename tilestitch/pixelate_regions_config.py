"""Re-export shim so callers can import from a dedicated config module."""
from tilestitch.tile_pixelate_regions import (
    PixelateRegionsConfig,
    PixelateRegionsError,
    pixelate_regions_config_from_env,
)

__all__ = [
    "PixelateRegionsConfig",
    "PixelateRegionsError",
    "pixelate_regions_config_from_env",
]
