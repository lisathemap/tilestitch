"""Configuration dataclass for tile palette settings."""
from __future__ import annotations

import os
from dataclasses import dataclass

from tilestitch.tile_palette import PaletteError, get_palette


@dataclass
class PaletteConfig:
    palette_name: str = "greyscale"
    apply_to_output: bool = False

    def __post_init__(self) -> None:
        # Validate that the palette exists
        try:
            get_palette(self.palette_name)
        except PaletteError as exc:
            raise PaletteError(str(exc)) from exc


def palette_config_from_env() -> PaletteConfig:
    name = os.environ.get("TILESTITCH_PALETTE", "greyscale").strip()
    apply = os.environ.get("TILESTITCH_PALETTE_APPLY", "false").strip().lower() == "true"
    return PaletteConfig(palette_name=name, apply_to_output=apply)
