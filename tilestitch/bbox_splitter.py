"""Utilities for splitting a bounding box into a grid of sub-bounding boxes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

BBox = Tuple[float, float, float, float]  # west, south, east, north


class BBoxSplitError(ValueError):
    """Raised when a bbox cannot be split as requested."""


@dataclass(frozen=True)
class BBoxGrid:
    """Result of splitting a bbox into rows x cols sub-boxes."""

    rows: int
    cols: int
    cells: List[BBox]

    def __len__(self) -> int:
        return len(self.cells)

    def __getitem__(self, index: int) -> BBox:
        return self.cells[index]

    def __iter__(self):
        return iter(self.cells)


def split_bbox(bbox: BBox, rows: int, cols: int) -> BBoxGrid:
    """Split *bbox* into a *rows* x *cols* grid of sub-bounding boxes.

    Parameters
    ----------
    bbox:
        (west, south, east, north) in degrees.
    rows:
        Number of vertical divisions (latitude axis).
    cols:
        Number of horizontal divisions (longitude axis).

    Returns
    -------
    BBoxGrid
        Ordered west→east, south→north.
    """
    if rows < 1 or cols < 1:
        raise BBoxSplitError(f"rows and cols must be >= 1, got rows={rows} cols={cols}")

    west, south, east, north = bbox

    if east <= west:
        raise BBoxSplitError(f"east ({east}) must be greater than west ({west})")
    if north <= south:
        raise BBoxSplitError(f"north ({north}) must be greater than south ({south})")

    lon_step = (east - west) / cols
    lat_step = (north - south) / rows

    cells: List[BBox] = []
    for row in range(rows):
        cell_south = south + row * lat_step
        cell_north = cell_south + lat_step
        for col in range(cols):
            cell_west = west + col * lon_step
            cell_east = cell_west + lon_step
            cells.append((cell_west, cell_south, cell_east, cell_north))

    return BBoxGrid(rows=rows, cols=cols, cells=cells)


def bbox_area(bbox: BBox) -> float:
    """Return the area of *bbox* in square degrees."""
    west, south, east, north = bbox
    return (east - west) * (north - south)


def bbox_center(bbox: BBox) -> Tuple[float, float]:
    """Return the (longitude, latitude) center of *bbox*."""
    west, south, east, north = bbox
    return ((west + east) / 2, (south + north) / 2)
