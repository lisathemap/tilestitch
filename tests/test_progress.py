"""Tests for tilestitch.progress."""

from __future__ import annotations

import io
import pytest

from tilestitch.progress import ProgressTracker, make_tracker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tracker(total: int = 4, label: str = "Test") -> tuple[ProgressTracker, io.StringIO]:
    buf = io.StringIO()
    t = ProgressTracker(total=total, label=label, stream=buf)
    return t, buf


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestProgressTrackerInit:
    def test_stores_total(self):
        t, _ = _tracker(10)
        assert t.total == 10

    def test_initial_completed_zero(self):
        t, _ = _tracker()
        assert t.completed == 0

    def test_initial_failed_zero(self):
        t, _ = _tracker()
        assert t.failed == 0

    def test_negative_total_raises(self):
        with pytest.raises(ValueError):
            _tracker(-1)


# ---------------------------------------------------------------------------
# Derived properties
# ---------------------------------------------------------------------------

class TestProgressTrackerProperties:
    def test_pending_equals_total_initially(self):
        t, _ = _tracker(5)
        assert t.pending == 5

    def test_percent_zero_initially(self):
        t, _ = _tracker(4)
        assert t.percent == 0.0

    def test_percent_100_when_total_zero(self):
        t, _ = _tracker(0)
        assert t.percent == 100.0

    def test_percent_50_after_half(self):
        t, _ = _tracker(4)
        t.advance()
        t.advance()
        assert t.percent == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# advance()
# ---------------------------------------------------------------------------

class TestAdvance:
    def test_increments_completed(self):
        t, _ = _tracker()
        t.advance()
        assert t.completed == 1

    def test_increments_failed(self):
        t, _ = _tracker()
        t.advance(failed=True)
        assert t.failed == 1

    def test_advance_writes_to_stream(self):
        t, buf = _tracker()
        t.advance()
        assert len(buf.getvalue()) > 0

    def test_render_contains_label(self):
        t, buf = _tracker(label="MyOp")
        t.advance()
        assert "MyOp" in buf.getvalue()

    def test_pending_decreases(self):
        t, _ = _tracker(4)
        t.advance()
        assert t.pending == 3


# ---------------------------------------------------------------------------
# finish()
# ---------------------------------------------------------------------------

def test_finish_writes_newline():
    t, buf = _tracker()
    t.finish()
    assert buf.getvalue().endswith("\n")


# ---------------------------------------------------------------------------
# make_tracker()
# ---------------------------------------------------------------------------

def test_make_tracker_returns_tracker():
    buf = io.StringIO()
    t = make_tracker(10, stream=buf)
    assert isinstance(t, ProgressTracker)


def test_make_tracker_uses_supplied_stream():
    buf = io.StringIO()
    t = make_tracker(2, stream=buf)
    t.advance()
    assert len(buf.getvalue()) > 0


def test_make_tracker_default_label():
    buf = io.StringIO()
    t = make_tracker(1, stream=buf)
    t.advance()
    assert "Fetching tiles" in buf.getvalue()
