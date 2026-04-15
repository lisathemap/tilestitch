"""Export stitched images to various formats including PNG and GeoTIFF."""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Optional

from PIL import Image

from tilestitch.tile_math import TileBounds


def _build_world_file_content(bounds: TileBounds, width: int, height: int) -> str:
    """Generate a world file (.pgw) string for georeferencing a PNG."""
    lon_per_pixel = (bounds.east - bounds.west) / width
    lat_per_pixel = (bounds.north - bounds.south) / height
    # World file format: pixel size x, rotation (0), rotation (0), -pixel size y, top-left x, top-left y
    lines = [
        f"{lon_per_pixel:.10f}",
        "0.0000000000",
        "0.0000000000",
        f"{-lat_per_pixel:.10f}",
        f"{bounds.west:.10f}",
        f"{bounds.north:.10f}",
    ]
    return "\n".join(lines) + "\n"


def export_png(
    image: Image.Image,
    output_path: str | Path,
    bounds: Optional[TileBounds] = None,
) -> Path:
    """Save image as PNG, optionally writing a world file for georeferencing."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG")

    if bounds is not None:
        world_path = output_path.with_suffix(".pgw")
        world_path.write_text(
            _build_world_file_content(bounds, image.width, image.height)
        )

    return output_path


def export_geotiff(
    image: Image.Image,
    output_path: str | Path,
    bounds: TileBounds,
) -> Path:
    """Save image as a GeoTIFF with embedded geographic metadata.

    Requires the 'tifffile' or 'rasterio' extra; falls back to a plain TIFF
    with a world file if neither is available.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import rasterio
        from rasterio.transform import from_bounds
        from rasterio.crs import CRS
        import numpy as np

        transform = from_bounds(
            bounds.west, bounds.south, bounds.east, bounds.north,
            image.width, image.height,
        )
        rgb = image.convert("RGB")
        data = np.array(rgb).transpose(2, 0, 1)  # CHW

        with rasterio.open(
            output_path,
            "w",
            driver="GTiff",
            height=image.height,
            width=image.width,
            count=3,
            dtype=data.dtype,
            crs=CRS.from_epsg(4326),
            transform=transform,
        ) as dst:
            dst.write(data)

    except ImportError:
        # Fallback: plain TIFF + world file
        tif_path = output_path.with_suffix(".tif")
        image.save(tif_path, format="TIFF")
        world_path = output_path.with_suffix(".tfw")
        world_path.write_text(
            _build_world_file_content(bounds, image.width, image.height)
        )
        return tif_path

    return output_path
