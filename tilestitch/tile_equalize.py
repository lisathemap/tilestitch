"""Histogram equalization filter for stitched tiles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from PIL import Image, ImageOps


class EqualizeError(Exception):
    """Raised when equalization cannot be applied."""


_VALID_MODES = ("full", "clahe")


@dataclass
class EqualizeConfig:
    enabled: bool = True
    mode: str = "full"
    mask: bool = False

    def __post_init__(self) -> None:
        self.mode = self.mode.strip().lower()
        if self.mode not in _VALID_MODES:
            raise EqualizeError(
                f"Unknown equalization mode {self.mode!r}; "
                f"expected one of {_VALID_MODES}"
            )


def equalize_config_from_env() -> EqualizeConfig:
    """Build an EqualizeConfig from environment variables."""
    import os

    raw_enabled = os.environ.get("TILESTITCH_EQUALIZE_ENABLED", "true")
    raw_mode = os.environ.get("TILESTITCH_EQUALIZE_MODE", "full")
    raw_mask = os.environ.get("TILESTITCH_EQUALIZE_MASK", "false")

    def _bool(v: str) -> bool:
        return v.strip().lower() in ("1", "true", "yes")

    return EqualizeConfig(
        enabled=_bool(raw_enabled),
        mode=raw_mode,
        mask=_bool(raw_mask),
    )


def apply_equalize(image: Image.Image, config: EqualizeConfig) -> Image.Image:
    """Apply histogram equalization to *image* according to *config*.

    Supports ``full`` (standard PIL equalization) and ``clahe``
    (contrast-limited, approximated via per-channel equalization on
    converted Lab-like split — kept dependency-free by operating on
    the L channel of an HSV-split as a close approximation).
    """
    if not config.enabled:
        return image

    original_mode = image.mode
    if image.mode not in ("RGB", "RGBA", "L"):
        image = image.convert("RGB")
        original_mode = "RGB"

    if config.mode == "full":
        if image.mode == "RGBA":
            r, g, b, a = image.split()
            rgb = Image.merge("RGB", (r, g, b))
            eq = ImageOps.equalize(rgb)
            er, eg, eb = eq.split()
            result = Image.merge("RGBA", (er, eg, eb, a))
        else:
            result = ImageOps.equalize(image)
        return result

    # clahe approximation: equalize only the V channel of HSV
    if image.mode == "RGBA":
        r, g, b, a = image.split()
        rgb = Image.merge("RGB", (r, g, b))
    else:
        rgb = image.convert("RGB") if image.mode == "L" else image
        a = None

    h, s, v = rgb.convert("HSV").split()
    v_eq = ImageOps.equalize(v)
    hsv_eq = Image.merge("HSV", (h, s, v_eq))
    rgb_eq = hsv_eq.convert("RGB")

    if a is not None:
        r2, g2, b2 = rgb_eq.split()
        result = Image.merge("RGBA", (r2, g2, b2, a))
    else:
        result = rgb_eq

    return result
