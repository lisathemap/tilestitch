"""Re-export :func:`glitch_config_from_env` for convenience."""

from tilestitch.tile_glitch import GlitchConfig, glitch_config_from_env  # noqa: F401

__all__ = ["GlitchConfig", "glitch_config_from_env"]
