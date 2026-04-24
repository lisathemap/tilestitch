"""Auto-level (auto white balance / stretch) adjustment for stitched tiles."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image, ImageOps


class AutolevelError(ValueError):
    """Raised when AutolevelConfig receives invalid parameters."""


@dataclass
class AutolevelConfig:
    """Configuration for the auto-level filter."""

    enabled: bool = True
    per_channel: bool = True  # stretch each channel independently
    cutoff: float = 0.0  # percentage of pixels to clip at each end (0.0–49.9)

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise AutolevelError("enabled must be a bool")
        if not isinstance(self.per_channel, bool):
            raise AutolevelError("per_channel must be a bool")
        if not (0.0 <= self.cutoff < 50.0):
            raise AutolevelError("cutoff must be in range [0.0, 50.0)")


def autolevel_config_from_env() -> AutolevelConfig:
    """Build an AutolevelConfig from environment variables."""
    import os

    def _bool(key: str, default: bool) -> bool:
        val = os.environ.get(key, "").strip().lower()
        if val == "":
            return default
        if val in ("1", "true", "yes"):
            return True
        if val in ("0", "false", "no"):
            return False
        raise AutolevelError(f"{key} must be a boolean value, got {val!r}")

    enabled = _bool("TILESTITCH_AUTOLEVEL_ENABLED", True)
    per_channel = _bool("TILESTITCH_AUTOLEVEL_PER_CHANNEL", True)
    cutoff_str = os.environ.get("TILESTITCH_AUTOLEVEL_CUTOFF", "0.0").strip()
    try:
        cutoff = float(cutoff_str)
    except ValueError:
        raise AutolevelError(f"TILESTITCH_AUTOLEVEL_CUTOFF must be a float, got {cutoff_str!r}")
    return AutolevelConfig(enabled=enabled, per_channel=per_channel, cutoff=cutoff)


def apply_autolevel(image: Image.Image, config: Optional[AutolevelConfig] = None) -> Image.Image:
    """Apply auto-level stretching to *image* and return the result."""
    if config is None:
        config = AutolevelConfig()
    if not config.enabled:
        return image

    src = image.convert("RGBA")
    r, g, b, a = src.split()

    if config.per_channel:
        r = ImageOps.autocontrast(r, cutoff=config.cutoff)
        g = ImageOps.autocontrast(g, cutoff=config.cutoff)
        b = ImageOps.autocontrast(b, cutoff=config.cutoff)
    else:
        rgb = Image.merge("RGB", (r, g, b))
        rgb = ImageOps.autocontrast(rgb, cutoff=config.cutoff)
        r, g, b = rgb.split()

    result = Image.merge("RGBA", (r, g, b, a))
    return result
