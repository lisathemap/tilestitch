"""Configuration for tile merging behaviour, resolved from env vars."""

from __future__ import annotations

import os
from dataclasses import dataclass

_VALID_STRATEGIES = frozenset({"first", "last", "error"})


@dataclass(frozen=True)
class TileMergerConfig:
    """Settings that control how overlapping tiles are resolved."""

    on_conflict: str = "first"

    def __post_init__(self) -> None:
        if self.on_conflict not in _VALID_STRATEGIES:
            raise ValueError(
                f"on_conflict must be one of {sorted(_VALID_STRATEGIES)}, "
                f"got {self.on_conflict!r}"
            )


def tile_merger_config_from_env() -> TileMergerConfig:
    """Build a :class:`TileMergerConfig` from environment variables.

    Environment variables
    ---------------------
    TILESTITCH_MERGE_CONFLICT
        Conflict resolution strategy: ``first`` (default), ``last``, or
        ``error``.
    """
    on_conflict = os.environ.get("TILESTITCH_MERGE_CONFLICT", "first").strip().lower()
    return TileMergerConfig(on_conflict=on_conflict)
