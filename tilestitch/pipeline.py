"""High-level pipeline orchestrating fetch → stitch → export."""

from __future__ import annotations

import os
from typing import Optional

from tilestitch.logger import get_logger
from tilestitch.validator import validate_bbox, validate_zoom
from tilestitch.tile_math import tiles_for_bbox
from tilestitch.sources import get_source, tile_url
from tilestitch.tile_fetcher import fetch_tiles
from tilestitch.stitcher import stitch_tiles, save_image
from tilestitch.exporter import export_png, export_geotiff
from tilestitch.metadata import build_metadata, save_metadata

logger = get_logger(__name__)


def run(
    bbox: tuple[float, float, float, float],
    zoom: int,
    source_name: str = "osm",
    output: str = "output.png",
    geotiff: bool = False,
    save_meta: bool = False,
    cache_dir: Optional[str] = None,
) -> None:
    """Execute the full tilestitch pipeline.

    Args:
        bbox: (min_lat, min_lon, max_lat, max_lon)
        zoom: Tile zoom level (0-19).
        source_name: Tile source identifier.
        output: Destination file path for the image.
        geotiff: When True, export as GeoTIFF instead of PNG.
        save_meta: When True, write a sidecar JSON metadata file.
        cache_dir: Optional directory for tile caching.
    """
    validate_bbox(bbox)
    validate_zoom(zoom)

    source = get_source(source_name)
    logger.info("Using source '%s' at zoom %d", source_name, zoom)

    bounds = tiles_for_bbox(*bbox, zoom)
    logger.info(
        "Tile bounds: x=[%d,%d] y=[%d,%d]",
        bounds.x_min, bounds.x_max,
        bounds.y_min, bounds.y_max,
    )

    urls = {
        (x, y): tile_url(source, x, y, zoom)
        for x in range(bounds.x_min, bounds.x_max + 1)
        for y in range(bounds.y_min, bounds.y_max + 1)
    }

    tile_data = fetch_tiles(urls)
    logger.info("Fetched %d tiles", len(tile_data))

    image = stitch_tiles(tile_data, bounds)
    logger.info("Stitched image size: %dx%d", image.width, image.height)

    if geotiff:
        export_geotiff(image, bounds, zoom, output)
        logger.info("Saved GeoTIFF: %s", output)
    else:
        export_png(image, output)
        logger.info("Saved PNG: %s", output)

    if save_meta:
        meta = build_metadata(
            source=source_name,
            zoom=zoom,
            bbox=bbox,
            bounds=bounds,
            image_width=image.width,
            image_height=image.height,
        )
        meta_path = os.path.splitext(output)[0] + ".json"
        save_metadata(meta, meta_path)
        logger.info("Saved metadata: %s", meta_path)
