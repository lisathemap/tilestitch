"""Dodge and burn adjustment for tile images."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from PIL import Image


class DodgeBurnError(Exception):
    """Raised when dodge/burn configuration or processing fails."""


@dataclass
class DodgeBurnConfig:
    """Configuration for dodge/burn adjustment."""

    mode: Literal["dodge", "burn"] = "dodge"
    factor: float = 0.5
    enabled: bool = True

    def __post_init__(self) -> None:
        self.mode = self.mode.strip().lower()
        if self.mode not in ("dodge", "burn"):
            raise DodgeBurnError(f"mode must be 'dodge' or 'burn', got: {self.mode!r}")
        if not (0.0 < self.factor <= 1.0):
            raise DodgeBurnError(f"factor must be in (0.0, 1.0], got: {self.factor}")


def dodge_burn_config_from_env(env: dict[str, str] | None = None) -> DodgeBurnConfig:
    """Build a DodgeBurnConfig from environment variables."""
    import os

    e = env if env is not None else os.environ
    mode = e.get("TILESTITCH_DODGE_BURN_MODE", "dodge").strip().lower()
    factor = float(e.get("TILESTITCH_DODGE_BURN_FACTOR", "0.5"))
    enabled = e.get("TILESTITCH_DODGE_BURN_ENABLED", "true").strip().lower() != "false"
    return DodgeBurnConfig(mode=mode, factor=factor, enabled=enabled)


def apply_dodge_burn(image: Image.Image, config: DodgeBurnConfig) -> Image.Image:
    """Apply dodge or burn adjustment to *image*."""
    if not config.enabled:
        return image

    src = image.convert("RGBA")
    arr = np.array(src, dtype=np.float32)
    rgb = arr[:, :, :3]

    if config.mode == "dodge":
        # Dodge: lighten by dividing by (1 - factor)
        divisor = 1.0 - config.factor
        if divisor < 1e-6:
            divisor = 1e-6
        rgb = np.clip(rgb / divisor, 0, 255)
    else:
        # Burn: darken by multiplying by (1 - factor)
        rgb = np.clip(rgb * (1.0 - config.factor), 0, 255)

    arr[:, :, :3] = rgb
    result = Image.fromarray(arr.astype(np.uint8), "RGBA")

    if image.mode != "RGBA":
        result = result.convert(image.mode)
    return result
