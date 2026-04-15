"""Rate limiting utilities for tile fetch requests."""

import time
import threading
from collections import defaultdict
from typing import Optional


class RateLimiter:
    """Token-bucket rate limiter, keyed by host."""

    def __init__(self, requests_per_second: float = 2.0):
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive")
        self._rps = requests_per_second
        self._interval = 1.0 / requests_per_second
        self._last_call: dict[str, float] = defaultdict(float)
        self._lock = threading.Lock()

    @property
    def requests_per_second(self) -> float:
        return self._rps

    def wait(self, host: str) -> None:
        """Block until the rate limit allows a new request for *host*."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call[host]
            wait_time = self._interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            self._last_call[host] = time.monotonic()

    def reset(self, host: Optional[str] = None) -> None:
        """Reset tracking state for *host*, or all hosts if None."""
        with self._lock:
            if host is None:
                self._last_call.clear()
            else:
                self._last_call.pop(host, None)


_default_limiter: Optional[RateLimiter] = None
_limiter_lock = threading.Lock()


def get_rate_limiter(requests_per_second: float = 2.0) -> RateLimiter:
    """Return the process-wide default :class:`RateLimiter`, creating it if needed."""
    global _default_limiter
    with _limiter_lock:
        if _default_limiter is None:
            _default_limiter = RateLimiter(requests_per_second)
    return _default_limiter


def set_rate_limiter(limiter: RateLimiter) -> None:
    """Replace the process-wide default limiter (useful in tests)."""
    global _default_limiter
    with _limiter_lock:
        _default_limiter = limiter
