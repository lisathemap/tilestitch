"""Retry helper for HTTP tile fetches."""

import time
import logging
from typing import Callable, Optional, Tuple, Type

from tilestitch.logger import get_logger

log = get_logger(__name__)


class RetryError(Exception):
    """Raised when all retry attempts are exhausted."""


def with_retry(
    fn: Callable[[], bytes],
    *,
    attempts: int = 3,
    backoff: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception], None]] = None,
) -> bytes:
    """Call *fn* up to *attempts* times, sleeping with exponential back-off.

    Parameters
    ----------
    fn:
        Zero-argument callable that returns raw tile bytes.
    attempts:
        Maximum number of tries (must be >= 1).
    backoff:
        Base sleep time in seconds; doubles on each failure.
    exceptions:
        Tuple of exception types that trigger a retry.
    on_retry:
        Optional callback invoked with ``(attempt_number, exception)``
        before sleeping.

    Returns
    -------
    bytes
        The return value of *fn* on success.

    Raises
    ------
    RetryError
        If every attempt raises one of *exceptions*.
    """
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    last_exc: Optional[Exception] = None
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except exceptions as exc:
            last_exc = exc
            log.warning("Attempt %d/%d failed: %s", attempt, attempts, exc)
            if on_retry is not None:
                on_retry(attempt, exc)
            if attempt < attempts:
                sleep_time = backoff * (2 ** (attempt - 1))
                log.debug("Retrying in %.2f s", sleep_time)
                time.sleep(sleep_time)

    raise RetryError(f"All {attempts} attempts failed") from last_exc
