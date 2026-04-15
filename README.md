# tilestitch

A CLI tool for stitching map tiles from multiple sources into a single exportable image or GeoTIFF.

---

## Installation

```bash
pip install tilestitch
```

Or install from source:

```bash
git clone https://github.com/yourname/tilestitch.git
cd tilestitch && pip install -e .
```

---

## Usage

Stitch tiles from a tile server URL into a single image:

```bash
tilestitch stitch \
  --source "https://tile.openstreetmap.org/{z}/{x}/{y}.png" \
  --bbox "-122.52,37.70,-122.35,37.83" \
  --zoom 13 \
  --output map.png
```

Export as a georeferenced GeoTIFF:

```bash
tilestitch stitch \
  --source "https://tile.openstreetmap.org/{z}/{x}/{y}.png" \
  --bbox "-122.52,37.70,-122.35,37.83" \
  --zoom 13 \
  --output map.tif \
  --format geotiff
```

### Options

| Flag | Description |
|------|-------------|
| `--source` | Tile server URL template `{z}/{x}/{y}` |
| `--bbox` | Bounding box as `min_lon,min_lat,max_lon,max_lat` |
| `--zoom` | Zoom level (0–19) |
| `--output` | Output file path |
| `--format` | Output format: `png`, `jpeg`, or `geotiff` (default: `png`) |
| `--concurrency` | Number of parallel tile downloads (default: 8) |

---

## Requirements

- Python 3.8+
- `Pillow`, `requests`, `rasterio` (installed automatically)

---

## License

This project is licensed under the [MIT License](LICENSE).