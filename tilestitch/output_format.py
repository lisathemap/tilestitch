"""Output format resolution and validation for tilestitch exports."""

from __future__ import annotations

from enum import Enum
from typing import Optional


class OutputFormat(str, Enum):
    PNG = "png"
    GEOTIFF = "geotiff"

    @classmethod
    def from_string(cls, value: str) -> "OutputFormat":
        """Parse a format string, case-insensitively."""
        normalised = value.strip().lower()
        try:
            return cls(normalised)
        except ValueError:
            supported = ", ".join(f.value for f in cls)
            raise OutputFormatError(
                f"Unsupported output format {value!r}. Supported: {supported}"
            )

    @property
    def extension(self) -> str:
        """Return the canonical file extension (without leading dot)."""
        return self.value if self != OutputFormat.GEOTIFF else "tif"

    @property
    def mime_type(self) -> str:
        _map = {
            OutputFormat.PNG: "image/png",
            OutputFormat.GEOTIFF: "image/tiff",
        }
        return _map[self]


class OutputFormatError(ValueError):
    """Raised when an unsupported or invalid output format is requested."""


def resolve_format(path: str, fmt: Optional[str] = None) -> OutputFormat:
    """Determine the output format from an explicit flag or the file extension.

    Parameters
    ----------
    path:
        Destination file path (used for extension inference).
    fmt:
        Explicit format string supplied by the caller (takes precedence).
    """
    if fmt:
        return OutputFormat.from_string(fmt)

    suffix = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    ext_map = {
        "png": OutputFormat.PNG,
        "tif": OutputFormat.GEOTIFF,
        "tiff": OutputFormat.GEOTIFF,
    }
    if suffix in ext_map:
        return ext_map[suffix]

    raise OutputFormatError(
        f"Cannot infer output format from path {path!r}. "
        "Provide --format explicitly or use a recognised extension (.png, .tif, .tiff)."
    )
