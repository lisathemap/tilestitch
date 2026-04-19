from __future__ import annotations

from dataclasses import dataclass
from PIL import Image, ImageOps
import os


class ColorizeError(ValueError):
    pass


def _parse_colour(value: str) -> str:
    value = value.strip()
    if not value.startswith("#") or len(value) not in (4, 7):
        raise ColorizeError(f"Invalid hex colour: {value!r}")
    return value


@dataclass
class ColorizeConfig:
    black: str = "#000000"
    white: str = "#ffffff"
    enabled: bool = True

    def __post_init__(self) -> None:
        self.black = _parse_colour(self.black)
        self.white = _parse_colour(self.white)
        if not isinstance(self.enabled, bool):
            raise ColorizeError("enabled must be a bool")


def colorize_config_from_env() -> ColorizeConfig:
    black = os.environ.get("TILESTITCH_COLORIZE_BLACK", "#000000")
    white = os.environ.get("TILESTITCH_COLORIZE_WHITE", "#ffffff")
    enabled = os.environ.get("TILESTITCH_COLORIZE_ENABLED", "true").lower() == "true"
    return ColorizeConfig(black=black, white=white, enabled=enabled)


def apply_colorize(image: Image.Image, config: ColorizeConfig) -> Image.Image:
    if not config.enabled:
        return image
    grey = image.convert("L")
    colourized = ImageOps.colorize(grey, black=config.black, white=config.white)
    if image.mode == "RGBA":
        colourized = colourized.convert("RGBA")
        r, g, b, _ = image.split()
        _, _, _, a = image.split()
        colourized.putalpha(a)
    return colourized
