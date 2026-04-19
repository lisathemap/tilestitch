"""Re-exports OverlayConfig for consistent import patterns."""
from tilestitch.tile_overlay import OverlayConfig, OverlayError, overlay_config_from_env

__all__ = ["OverlayConfig", "OverlayError", "overlay_config_from_env"]
