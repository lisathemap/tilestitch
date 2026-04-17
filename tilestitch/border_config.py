"""Standalone dataclass re-export and factory helpers for border configuration.

Keeps the same pattern as other *_config modules in the project so that
pipeline.py can import a uniform interface.
"""
from __future__ import annotations

from tilestitch.tile_border import BorderConfig, BorderError, border_config_from_env

__all__ = ["BorderConfig", "BorderError", "border_config_from_env"]
