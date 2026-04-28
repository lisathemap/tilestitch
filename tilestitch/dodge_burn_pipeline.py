"""Pipeline stage for dodge/burn adjustment."""

from __future__ import annotations

from PIL import Image

from tilestitch.tile_dodge_burn import (
    DodgeBurnConfig,
    apply_dodge_burn,
    dodge_burn_config_from_env,
)


class DodgeBurnStage:
    """Applies dodge or burn adjustment as a pipeline stage."""

    def __init__(self, config: DodgeBurnConfig | None) -> None:
        self._config = config

    def process(self, image: Image.Image) -> Image.Image:
        if self._config is None or not self._config.enabled:
            return image
        return apply_dodge_burn(image, self._config)


def build_dodge_burn_stage(
    env: dict[str, str] | None = None,
) -> DodgeBurnStage:
    """Construct a DodgeBurnStage from environment variables."""
    try:
        config = dodge_burn_config_from_env(env)
    except Exception:
        config = None
    return DodgeBurnStage(config)
