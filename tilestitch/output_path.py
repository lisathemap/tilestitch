"""Utilities for resolving and validating output file paths."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from tilestitch.output_format import OutputFormat, resolve_format


class OutputPathError(OSError):
    """Raised when an output path cannot be used."""


def resolve_output_path(
    path: str,
    fmt: Optional[str] = None,
    *,
    create_parents: bool = True,
) -> Path:
    """Resolve, validate and optionally prepare an output path.

    Parameters
    ----------
    path:
        Raw output path supplied by the user.
    fmt:
        Explicit format override; if omitted the extension is used.
    create_parents:
        When *True* (default) any missing parent directories are created.

    Returns
    -------
    Path
        An absolute :class:`pathlib.Path` ready for writing.
    """
    output = Path(path).expanduser().resolve()

    # Ensure the format is resolvable before touching the filesystem.
    resolved_fmt: OutputFormat = resolve_format(str(output), fmt)

    # Append the canonical extension if the path has none or a wrong one.
    expected_ext = f".{resolved_fmt.extension}"
    if output.suffix.lower() not in (".png", ".tif", ".tiff"):
        output = output.with_suffix(expected_ext)

    if create_parents:
        output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists() and not os.access(output, os.W_OK):
        raise OutputPathError(f"Output path is not writable: {output}")

    if not os.access(output.parent, os.W_OK):
        raise OutputPathError(f"Output directory is not writable: {output.parent}")

    return output
