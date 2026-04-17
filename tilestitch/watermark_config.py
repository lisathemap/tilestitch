"""Thin re-export shim so pipeline can import from a dedicated config module."""
from tilestitch.tile_watermark import WatermarkConfig, watermark_config_from_env

__all__ = ["WatermarkConfig", "watermark_config_from_env"]
