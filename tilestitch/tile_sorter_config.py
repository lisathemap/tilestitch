"""Configuration dataclass for tile sort order."""

from __future__ import annotations

import os
from dataclasses import dataclass

from tilestitch.tile_sorter import SortOrder

_ENV_KEY = "TILESTITCH_SORT_ORDER"
_DEFAULT = SortOrder.ROW_MAJOR


@dataclass(frozen=True)
class TileSorterConfig:
    order: SortOrder = _DEFAULT

    def __post_init__(self) -> None:
        if not isinstance(self.order, SortOrder):
            raise TypeError(f"order must be a SortOrder, got {type(self.order)}")


def tile_sorter_config_from_env() -> TileSorterConfig:
    """Build a :class:`TileSorterConfig` from environment variables.

    ``TILESTITCH_SORT_ORDER`` — one of ``row_major``, ``col_major``, ``hilbert``
    (default: ``row_major``).
    """
    raw = os.environ.get(_ENV_KEY, _DEFAULT.value)
    order = SortOrder.from_string(raw)
    return TileSorterConfig(order=order)
