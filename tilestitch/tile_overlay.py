"""Overlay a semi-transparent image on top of a tile image."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image


class OverlayError(Exception):
    """Raised when overlay configuration or application fails."""


@dataclass
class OverlayConfig:
    path: Path
    opacity: float = 1.0
    enabled: bool = True

    def __post_init__(self) -> None:
        self.path = Path(self.path)
        if not self.path.exists():
            raise OverlayError(f"Overlay file not found: {self.path}")
        if not (0.0 <= self.opacity <= 1.0):
            raise OverlayError("opacity must be between 0.0 and 1.0")


def overlay_config_from_env() -> OverlayConfig | None:
    import os
    path_str = os.environ.get("TILESTITCH_OVERLAY_PATH", "")
    if not path_str:
        return None
    opacity = float(os.environ.get("TILESTITCH_OVERLAY_OPACITY", "1.0"))
    enabled = os.environ.get("TILESTITCH_OVERLAY_ENABLED", "true").lower() == "true"
    return OverlayConfig(path=Path(path_str), opacity=opacity, enabled=enabled)


def apply_overlay(image: Image.Image, config: OverlayConfig) -> Image.Image:
    """Composite an overlay image onto *image* with the given opacity."""
    if not config.enabled:
        return image

    overlay = Image.open(config.path).convert("RGBA")
    overlay = overlay.resize(image.size, Image.LANCZOS)

    if config.opacity < 1.0:
        r, g, b, a = overlay.split()
        a = a.point(lambda v: int(v * config.opacity))
        overlay = Image.merge("RGBA", (r, g, b, a))

    base = image.convert("RGBA")
    combined = Image.alpha_composite(base, overlay)
    return combined.convert(image.mode) if image.mode != "RGBA" else combined
