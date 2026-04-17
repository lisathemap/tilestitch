"""Configuration for the tile cropper."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class CropConfig:
    enabled: bool = True
    tile_size: int = 256

    def __post_init__(self) -> None:
        if self.tile_size <= 0:
            raise ValueError(f"tile_size must be positive, got {self.tile_size}")


def crop_config_from_env() -> CropConfig:
    """Build a CropConfig from environment variables.

    TILESTITCH_CROP_ENABLED  — '0' or 'false' to disable (default enabled)
    TILESTITCH_CROP_TILE_SIZE — integer pixel size (default 256)
    """
    raw_enabled = os.environ.get("TILESTITCH_CROP_ENABLED", "true")
    enabled = raw_enabled.strip().lower() not in ("0", "false", "no")

    tile_size = int(os.environ.get("TILESTITCH_CROP_TILE_SIZE", "256"))

    return CropConfig(enabled=enabled, tile_size=tile_size)
