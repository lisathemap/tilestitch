from __future__ import annotations

import os
from dataclasses import dataclass
from PIL import Image, ImageOps


class PaddingError(Exception):
    pass


@dataclass
class PaddingConfig:
    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0
    color: str = "white"

    def __post_init__(self) -> None:
        for name, val in [("top", self.top), ("right", self.right),
                          ("bottom", self.bottom), ("left", self.left)]:
            if not isinstance(val, int) or val < 0:
                raise PaddingError(f"{name} padding must be a non-negative integer, got {val!r}")
        if not self.color or not self.color.strip():
            raise PaddingError("color must be a non-empty string")

    @property
    def any_set(self) -> bool:
        return any([self.top, self.right, self.bottom, self.left])


def apply_padding(image: Image.Image, config: PaddingConfig) -> Image.Image:
    """Return a new image with uniform or asymmetric padding applied."""
    if not config.any_set:
        return image
    border = (config.left, config.top, config.right, config.bottom)
    try:
        return ImageOps.expand(image, border=border, fill=config.color)
    except (ValueError, KeyError) as exc:
        raise PaddingError(f"Invalid padding color {config.color!r}: {exc}") from exc


def padding_config_from_env() -> PaddingConfig:
    """Build a PaddingConfig from environment variables."""
    def _int(key: str, default: int) -> int:
        raw = os.environ.get(key, "").strip()
        return int(raw) if raw else default

    return PaddingConfig(
        top=_int("TILESTITCH_PADDING_TOP", 0),
        right=_int("TILESTITCH_PADDING_RIGHT", 0),
        bottom=_int("TILESTITCH_PADDING_BOTTOM", 0),
        left=_int("TILESTITCH_PADDING_LEFT", 0),
        color=os.environ.get("TILESTITCH_PADDING_COLOR", "white").strip() or "white",
    )
