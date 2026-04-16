"""Configuration for tile/image scaling, resolved from env vars or defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass

from tilestitch.tile_scaler import ScaleMethod, ScaleMethodError

_DEFAULT_TILE_SIZE = 256
_DEFAULT_SCALE_FACTOR = 1.0
_DEFAULT_METHOD = ScaleMethod.LANCZOS


@dataclass(frozen=True)
class ScaleConfig:
    """Immutable scaling configuration."""

    tile_size: int
    scale_factor: float
    method: ScaleMethod

    def __post_init__(self) -> None:
        if self.tile_size <= 0:
            raise ValueError(f"tile_size must be positive, got {self.tile_size}")
        if self.scale_factor <= 0:
            raise ValueError(f"scale_factor must be positive, got {self.scale_factor}")


def scale_config_from_env() -> ScaleConfig:
    """Build a ScaleConfig from environment variables.

    Environment variables:
        TILESTITCH_TILE_SIZE   – integer pixel size for individual tiles (default 256)
        TILESTITCH_SCALE       – float output scale factor (default 1.0)
        TILESTITCH_SCALE_METHOD – resampling method name (default lanczos)
    """
    tile_size = int(os.environ.get("TILESTITCH_TILE_SIZE", _DEFAULT_TILE_SIZE))
    scale_factor = float(os.environ.get("TILESTITCH_SCALE", _DEFAULT_SCALE_FACTOR))

    raw_method = os.environ.get("TILESTITCH_SCALE_METHOD", _DEFAULT_METHOD.value)
    try:
        method = ScaleMethod.from_string(raw_method)
    except ScaleMethodError:
        method = _DEFAULT_METHOD

    return ScaleConfig(tile_size=tile_size, scale_factor=scale_factor, method=method)
