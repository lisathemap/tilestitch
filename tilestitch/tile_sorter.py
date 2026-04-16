"""Utilities for sorting tile keys into deterministic render order."""

from __future__ import annotations

from enum import Enum
from typing import Iterable

from tilestitch.tile_math import TileBounds


class SortOrder(str, Enum):
    ROW_MAJOR = "row_major"      # left-to-right, top-to-bottom
    COL_MAJOR = "col_major"      # top-to-bottom, left-to-right
    HILBERT = "hilbert"          # approximate locality-preserving order

    @classmethod
    def from_string(cls, value: str) -> "SortOrder":
        normalised = value.strip().lower()
        for member in cls:
            if member.value == normalised:
                return member
        raise SortOrderError(f"Unknown sort order: {value!r}")


class SortOrderError(ValueError):
    pass


def _hilbert_d(n: int, x: int, y: int) -> int:
    """Return the Hilbert curve distance for grid of side *n* (power of 2)."""
    d = 0
    s = n // 2
    while s > 0:
        rx = 1 if (x & s) > 0 else 0
        ry = 1 if (y & s) > 0 else 0
        d += s * s * ((3 * rx) ^ ry)
        # rotate
        if ry == 0:
            if rx == 1:
                x = s - 1 - x
                y = s - 1 - y
            x, y = y, x
        s //= 2
    return d


def sort_tiles(
    keys: Iterable[tuple[int, int, int]],
    bounds: TileBounds,
    order: SortOrder = SortOrder.ROW_MAJOR,
) -> list[tuple[int, int, int]]:
    """Return *keys* sorted according to *order*.

    Parameters
    ----------
    keys:   iterable of (z, x, y) tile keys
    bounds: TileBounds used to normalise coordinates for Hilbert ordering
    order:  desired SortOrder
    """
    key_list = list(keys)

    if order == SortOrder.ROW_MAJOR:
        return sorted(key_list, key=lambda t: (t[2], t[1]))

    if order == SortOrder.COL_MAJOR:
        return sorted(key_list, key=lambda t: (t[1], t[2]))

    if order == SortOrder.HILBERT:
        width = max(bounds.x_max - bounds.x_min, 1)
        height = max(bounds.y_max - bounds.y_min, 1)
        n = 1
        while n < max(width, height):
            n *= 2
        def _key(t: tuple[int, int, int]) -> int:
            lx = t[1] - bounds.x_min
            ly = t[2] - bounds.y_min
            return _hilbert_d(n, lx, ly)
        return sorted(key_list, key=_key)

    raise SortOrderError(f"Unhandled order: {order}")
