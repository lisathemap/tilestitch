"""Command-line interface for tilestitch."""

import argparse
import sys

from tilestitch.pipeline import run
from tilestitch.sources import list_sources


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tilestitch",
        description="Stitch map tiles from multiple sources into a single image or GeoTIFF.",
    )

    parser.add_argument(
        "--bbox",
        required=True,
        metavar=("MIN_LAT", "MIN_LON", "MAX_LAT", "MAX_LON"),
        nargs=4,
        type=float,
        help="Bounding box as min_lat min_lon max_lat max_lon.",
    )
    parser.add_argument(
        "--zoom",
        required=True,
        type=int,
        help="Zoom level (0-19).",
    )
    parser.add_argument(
        "--source",
        default="osm",
        help="Tile source identifier (default: osm). Use --list-sources to see available options.",
    )
    parser.add_argument(
        "--output",
        default="output.png",
        help="Output file path (default: output.png). Use .tif/.tiff for GeoTIFF export.",
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="List available tile sources and exit.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=8,
        help="Number of concurrent tile fetch workers (default: 8).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_sources:
        print("Available tile sources:")
        for name, description in list_sources():
            print(f"  {name:<20} {description}")
        return 0

    min_lat, min_lon, max_lat, max_lon = args.bbox

    if min_lat >= max_lat:
        print("Error: min_lat must be less than max_lat.", file=sys.stderr)
        return 1
    if min_lon >= max_lon:
        print("Error: min_lon must be less than max_lon.", file=sys.stderr)
        return 1
    if not (0 <= args.zoom <= 19):
        print("Error: zoom must be between 0 and 19.", file=sys.stderr)
        return 1

    try:
        run(
            bbox=(min_lat, min_lon, max_lat, max_lon),
            zoom=args.zoom,
            source=args.source,
            output=args.output,
            concurrency=args.concurrency,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Saved to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
