"""High-level output writer that dispatches to the correct exporter."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image

from tilestitch.exporter import export_geotiff, export_png
from tilestitch.output_format import OutputFormat, resolve_format
from tilestitch.output_path import resolve_output_path
from tilestitch.tile_math import TileBounds


def write_output(
    image: Image.Image,
    bounds: TileBounds,
    path: str,
    fmt: Optional[str] = None,
    *,
    create_parents: bool = True,
) -> Path:
    """Write *image* to *path* in the appropriate format.

    Parameters
    ----------
    image:
        Stitched PIL image to export.
    bounds:
        Tile bounds describing the geographic extent of the image.
    path:
        Destination path (extension may be used to infer format).
    fmt:
        Explicit format override (``'png'`` or ``'geotiff'``).
    create_parents:
        Create missing parent directories when *True* (default).

    Returns
    -------
    Path
        The resolved, absolute path that was written.
    """
    output_path = resolve_output_path(path, fmt, create_parents=create_parents)
    output_format = resolve_format(str(output_path), fmt)

    if output_format == OutputFormat.PNG:
        export_png(image, str(output_path), bounds)
    elif output_format == OutputFormat.GEOTIFF:
        export_geotiff(image, str(output_path), bounds)
    else:  # pragma: no cover
        raise ValueError(f"Unhandled output format: {output_format}")

    return output_path
