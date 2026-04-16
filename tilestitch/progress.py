"""Progress reporting for tile fetch and stitch operations."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Optional, TextIO


@dataclass
class ProgressTracker:
    """Tracks progress of a multi-step operation and reports to a stream."""

    total: int
    label: str = "Progress"
    stream: TextIO = field(default_factory=lambda: sys.stderr)
    _completed: int = field(default=0, init=False)
    _failed: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.total < 0:
            raise ValueError("total must be >= 0")

    @property
    def completed(self) -> int:
        return self._completed

    @property
    def failed(self) -> int:
        return self._failed

    @property
    def pending(self) -> int:
        return self.total - self._completed - self._failed

    @property
    def percent(self) -> float:
        if self.total == 0:
            return 100.0
        return (self._completed + self._failed) / self.total * 100.0

    def advance(self, *, failed: bool = False) -> None:
        """Record one step as done (success or failure) and redraw."""
        if failed:
            self._failed += 1
        else:
            self._completed += 1
        self._render()

    def finish(self) -> None:
        """Print a final newline to end the progress line."""
        self.stream.write("\n")
        self.stream.flush()

    def _render(self) -> None:
        done = self._completed + self._failed
        bar_width = 30
        filled = int(bar_width * done / max(self.total, 1))
        bar = "#" * filled + "-" * (bar_width - filled)
        line = (
            f"\r{self.label}: [{bar}] {done}/{self.total}"
            f" ({self.percent:.0f}%)"
            f" ok={self._completed} err={self._failed}"
        )
        self.stream.write(line)
        self.stream.flush()


def make_tracker(
    total: int,
    label: str = "Fetching tiles",
    stream: Optional[TextIO] = None,
) -> ProgressTracker:
    """Convenience factory; uses stderr when no stream is supplied."""
    return ProgressTracker(
        total=total,
        label=label,
        stream=stream if stream is not None else sys.stderr,
    )
