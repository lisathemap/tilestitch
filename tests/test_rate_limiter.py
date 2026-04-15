"""Tests for tilestitch.rate_limiter."""

import time
import threading
import pytest

from tilestitch.rate_limiter import (
    RateLimiter,
    get_rate_limiter,
    set_rate_limiter,
)


class TestRateLimiterInit:
    def test_stores_rps(self):
        rl = RateLimiter(5.0)
        assert rl.requests_per_second == 5.0

    def test_zero_rps_raises(self):
        with pytest.raises(ValueError, match="positive"):
            RateLimiter(0)

    def test_negative_rps_raises(self):
        with pytest.raises(ValueError):
            RateLimiter(-1.0)


class TestRateLimiterWait:
    def test_first_call_does_not_block_significantly(self):
        rl = RateLimiter(requests_per_second=100.0)
        start = time.monotonic()
        rl.wait("example.com")
        elapsed = time.monotonic() - start
        assert elapsed < 0.05

    def test_second_call_is_throttled(self):
        rl = RateLimiter(requests_per_second=10.0)  # 100 ms between calls
        rl.wait("host.test")
        start = time.monotonic()
        rl.wait("host.test")
        elapsed = time.monotonic() - start
        assert elapsed >= 0.08  # allow a little slack

    def test_different_hosts_are_independent(self):
        rl = RateLimiter(requests_per_second=10.0)
        rl.wait("host-a.test")
        # host-b has never been called, so it should not block
        start = time.monotonic()
        rl.wait("host-b.test")
        elapsed = time.monotonic() - start
        assert elapsed < 0.05

    def test_thread_safety(self):
        """Multiple threads should not raise exceptions."""
        rl = RateLimiter(requests_per_second=50.0)
        errors = []

        def _call():
            try:
                rl.wait("shared.host")
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [threading.Thread(target=_call) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []


class TestRateLimiterReset:
    def test_reset_specific_host_clears_state(self):
        rl = RateLimiter(requests_per_second=10.0)
        rl.wait("myhost")
        rl.reset("myhost")
        # After reset the next call should not block
        start = time.monotonic()
        rl.wait("myhost")
        elapsed = time.monotonic() - start
        assert elapsed < 0.05

    def test_reset_all_clears_all_hosts(self):
        rl = RateLimiter(requests_per_second=10.0)
        rl.wait("a")
        rl.wait("b")
        rl.reset()
        start = time.monotonic()
        rl.wait("a")
        elapsed = time.monotonic() - start
        assert elapsed < 0.05


class TestGetSetRateLimiter:
    def test_returns_rate_limiter_instance(self):
        rl = get_rate_limiter()
        assert isinstance(rl, RateLimiter)

    def test_same_instance_returned_twice(self):
        rl1 = get_rate_limiter()
        rl2 = get_rate_limiter()
        assert rl1 is rl2

    def test_set_rate_limiter_replaces_default(self):
        custom = RateLimiter(99.0)
        set_rate_limiter(custom)
        assert get_rate_limiter() is custom
        # restore a fresh default for other tests
        set_rate_limiter(RateLimiter(2.0))
