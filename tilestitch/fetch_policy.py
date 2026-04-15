"""Combines rate limiting and retry behaviour for tile fetching."""

from urllib.parse import urlparse
from typing import Callable, Optional

from tilestitch.rate_limiter import RateLimiter, get_rate_limiter
from tilestitch.retry import with_retry, RetryError  # noqa: F401 – re-exported
from tilestitch.logger import get_logger

log = get_logger(__name__)


class FetchPolicy:
    """Wraps a raw fetch callable with rate limiting and automatic retries.

    Parameters
    ----------
    attempts:
        How many times to try a failing request.
    backoff:
        Base back-off time (seconds) passed to :func:`~tilestitch.retry.with_retry`.
    limiter:
        :class:`~tilestitch.rate_limiter.RateLimiter` to use.  Defaults to
        the process-wide limiter returned by :func:`get_rate_limiter`.
    """

    def __init__(
        self,
        attempts: int = 3,
        backoff: float = 0.5,
        limiter: Optional[RateLimiter] = None,
    ) -> None:
        self.attempts = attempts
        self.backoff = backoff
        self._limiter = limiter or get_rate_limiter()

    @property
    def limiter(self) -> RateLimiter:
        return self._limiter

    def fetch(self, url: str, raw_fetch: Callable[[str], bytes]) -> bytes:
        """Fetch *url* respecting rate limits and retrying on failure.

        Parameters
        ----------
        url:
            Full tile URL.
        raw_fetch:
            Callable that accepts a URL string and returns raw bytes.
            Should raise an :class:`OSError` / :class:`IOError` on
            transient failures.
        """
        host = urlparse(url).hostname or url
        log.debug("Fetching %s (host=%s)", url, host)

        def _do_fetch() -> bytes:
            self._limiter.wait(host)
            return raw_fetch(url)

        return with_retry(
            _do_fetch,
            attempts=self.attempts,
            backoff=self.backoff,
            exceptions=(OSError, IOError),
        )


_default_policy: Optional[FetchPolicy] = None


def get_fetch_policy() -> FetchPolicy:
    """Return (or lazily create) the process-wide :class:`FetchPolicy`."""
    global _default_policy
    if _default_policy is None:
        _default_policy = FetchPolicy()
    return _default_policy


def set_fetch_policy(policy: FetchPolicy) -> None:
    """Replace the process-wide fetch policy (useful in tests)."""
    global _default_policy
    _default_policy = policy
