"""Configuration for the tile compositor."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class CompositorConfig:
    background: Tuple[int, int, int, int] = field(default=(0, 0, 0, 0))
    default_opacity: float = 1.0
    auto_size: bool = True

    def __post_init__(self) -> None:
        if not (0.0 <= self.default_opacity <= 1.0):
            raise ValueError(f"default_opacity must be 0-1, got {self.default_opacity}")
        if len(self.background) != 4:
            raise ValueError("background must be an RGBA tuple of length 4")


def compositor_config_from_env() -> CompositorConfig:
    opacity = float(os.environ.get("TILESTITCH_COMPOSITOR_OPACITY", "1.0"))
    auto = os.environ.get("TILESTITCH_COMPOSITOR_AUTO_SIZE", "true").lower() != "false"
    bg_raw = os.environ.get("TILESTITCH_COMPOSITOR_BG", "0,0,0,0")
    bg = tuple(int(v) for v in bg_raw.split(","))  # type: ignore[assignment]
    return CompositorConfig(background=bg, default_opacity=opacity, auto_size=auto)  # type: ignore[arg-type]
