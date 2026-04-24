"""Pipeline stage that applies the glitch effect to a stitched image."""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from tilestitch.tile_glitch import GlitchConfig, apply_glitch


@dataclass
class GlitchStage:
    """Wraps :func:`apply_glitch` as a pipeline stage."""

    config: GlitchConfig | None

    def process(self, image: Image.Image) -> Image.Image:
        """Apply glitch effect if enabled; otherwise return *image* unchanged."""
        if self.config is None or not self.config.enabled:
            return image
        return apply_glitch(image, self.config)


def build_glitch_stage(config: GlitchConfig | None = None) -> GlitchStage:
    """Construct a :class:`GlitchStage` from *config*.

    If *config* is ``None`` the stage is a no-op.
    """
    return GlitchStage(config=config)
