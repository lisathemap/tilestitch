"""Configuration helpers for progress reporting behaviour."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProgressConfig:
    """Controls whether and how progress is displayed."""

    enabled: bool = True
    label: str = "Fetching tiles"
    stream_name: str = "stderr"  # "stderr" | "stdout" | "none"

    def is_visible(self) -> bool:
        """Return *True* when progress output should actually be shown."""
        return self.enabled and self.stream_name != "none"


_ENV_DISABLE = "TILESTITCH_NO_PROGRESS"
_ENV_STREAM = "TILESTITCH_PROGRESS_STREAM"


def progress_config_from_env(
    default_label: str = "Fetching tiles",
    override_enabled: Optional[bool] = None,
) -> ProgressConfig:
    """Build a :class:`ProgressConfig` from environment variables.

    ``TILESTITCH_NO_PROGRESS=1``  → disable progress entirely.
    ``TILESTITCH_PROGRESS_STREAM`` → ``stderr`` (default) or ``stdout``.
    """
    disabled_by_env = os.environ.get(_ENV_DISABLE, "").strip() in {"1", "true", "yes"}
    stream = os.environ.get(_ENV_STREAM, "stderr").strip().lower()
    if stream not in {"stderr", "stdout", "none"}:
        stream = "stderr"

    enabled: bool
    if override_enabled is not None:
        enabled = override_enabled
    else:
        enabled = not disabled_by_env

    return ProgressConfig(
        enabled=enabled,
        label=default_label,
        stream_name=stream,
    )


def resolve_stream(config: ProgressConfig):
    """Return the actual stream object for *config*, or *None* when silent."""
    import sys

    if not config.is_visible():
        return None
    return sys.stderr if config.stream_name == "stderr" else sys.stdout
