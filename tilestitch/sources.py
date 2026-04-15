"""Predefined tile source URL templates and helpers."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class TileSource:
    """Describes a tile map service source."""

    name: str
    url_template: str
    attribution: str
    max_zoom: int = 19
    min_zoom: int = 0
    subdomains: Optional[str] = None  # e.g. "abc" for {s} substitution

    def tile_url(self, x: int, y: int, zoom: int, subdomain: str = "a") -> str:
        """Build a concrete tile URL.

        Args:
            x: Tile X coordinate.
            y: Tile Y coordinate.
            zoom: Zoom level.
            subdomain: Subdomain character if the template uses {s}.

        Returns:
            Fully resolved URL string.
        """
        url = self.url_template.format(x=x, y=y, z=zoom, s=subdomain)
        return url


# ---------------------------------------------------------------------------
# Built-in sources
# ---------------------------------------------------------------------------

OSM = TileSource(
    name="openstreetmap",
    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution="© OpenStreetMap contributors",
    max_zoom=19,
)

STADIA_ALIDADE_SMOOTH = TileSource(
    name="stadia_alidade_smooth",
    url_template="https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}.png",
    attribution="© Stadia Maps, © OpenMapTiles, © OpenStreetMap contributors",
    max_zoom=20,
)

CARTO_POSITRON = TileSource(
    name="carto_positron",
    url_template="https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
    attribution="© CARTO, © OpenStreetMap contributors",
    max_zoom=19,
)

CARTO_DARK_MATTER = TileSource(
    name="carto_dark_matter",
    url_template="https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
    attribution="© CARTO, © OpenStreetMap contributors",
    max_zoom=19,
)

_REGISTRY: Dict[str, TileSource] = {
    src.name: src
    for src in [OSM, STADIA_ALIDADE_SMOOTH, CARTO_POSITRON, CARTO_DARK_MATTER]
}


def get_source(name: str) -> TileSource:
    """Retrieve a built-in TileSource by name.

    Args:
        name: Source identifier string (case-insensitive).

    Returns:
        Matching TileSource instance.

    Raises:
        KeyError: If the source name is not registered.
    """
    key = name.lower()
    if key not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        raise KeyError(f"Unknown tile source '{name}'. Available: {available}")
    return _REGISTRY[key]


def list_sources() -> list:
    """Return names of all registered tile sources."""
    return sorted(_REGISTRY.keys())
