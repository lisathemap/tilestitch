"""Integrate watermark step into an image pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image

from tilestitch.tile_watermark import WatermarkConfig, apply_watermark


@dataclass
class WatermarkStage:
    """A pipeline stage that conditionally applies a watermark."""

    config: Optional[WatermarkConfig]
    enabled: bool = True

    def process(self, image: Image.Image) -> Image.Image:
        """Return image with watermark applied if enabled and config present."""
        if not self.enabled or self.config is None:
            return image
        return apply_watermark(image, self.config)


def build_watermark_stage(
    text: Optional[str] = None,
    enabled: bool = True,
    **kwargs,
) -> WatermarkStage:
    """Convenience factory; returns a disabled stage when *text* is None."""
    if text is None:
        return WatermarkStage(config=None, enabled=False)
    config = WatermarkConfig(text=text, **kwargs)
    return WatermarkStage(config=config, enabled=enabled)
