"""Tests for tilestitch.retry."""

import pytest
from unittest.mock import MagicMock, patch

from tilestitch.retry import with_retry, RetryError


class TestWithRetrySuccess:
    def test_returns_bytes_on_first_attempt(self):
        fn = MagicMock(return_value=b"tile-data")
        result = with_retry(fn, attempts=3)
        assert result == b"tile-data"
        fn.assert_called_once()

    def test_succeeds_on_second_attempt(self):
        fn = MagicMock(side_effect=[OSError("timeout"), b"ok"])
        with patch("tilestitch.retry.time.sleep"):
            result = with_retry(fn, attempts=3, exceptions=(OSError,))
        assert result == b"ok"
        assert fn.call_count == 2

    def test_succeeds_on_last_attempt(self):
        fn = MagicMock(side_effect=[ValueError(), ValueError(), b"data"])
        with patch("tilestitch.retry.time.sleep"):
            result = with_retry(fn, attempts=3, exceptions=(ValueError,))
        assert result == b"data"


class TestWithRetryFailure:
    def test_raises_retry_error_after_exhaustion(self):
        fn = MagicMock(side_effect=ConnectionError("refused"))
        with patch("tilestitch.retry.time.sleep"):
            with pytest.raises(RetryError):
                with_retry(fn, attempts=3, exceptions=(ConnectionError,))
        assert fn.call_count == 3

    def test_retry_error_chains_original_exception(self):
        original = RuntimeError("boom")
        fn = MagicMock(side_effect=original)
        with patch("tilestitch.retry.time.sleep"):
            with pytest.raises(RetryError) as exc_info:
                with_retry(fn, attempts=2, exceptions=(RuntimeError,))
        assert exc_info.value.__cause__ is original

    def test_non_matching_exception_propagates_immediately(self):
        fn = MagicMock(side_effect=TypeError("bad type"))
        with pytest.raises(TypeError):
            with_retry(fn, attempts=3, exceptions=(OSError,))
        fn.assert_called_once()

    def test_zero_attempts_raises_value_error(self):
        with pytest.raises(ValueError, match="attempts"):
            with_retry(lambda: b"", attempts=0)


class TestWithRetryBackoff:
    def test_sleep_called_between_attempts(self):
        fn = MagicMock(side_effect=[OSError(), b"ok"])
        with patch("tilestitch.retry.time.sleep") as mock_sleep:
            with_retry(fn, attempts=3, backoff=1.0, exceptions=(OSError,))
        mock_sleep.assert_called_once_with(1.0)  # 1.0 * 2^0

    def test_exponential_backoff_values(self):
        fn = MagicMock(side_effect=[OSError(), OSError(), b"ok"])
        with patch("tilestitch.retry.time.sleep") as mock_sleep:
            with_retry(fn, attempts=3, backoff=0.5, exceptions=(OSError,))
        calls = [c.args[0] for c in mock_sleep.call_args_list]
        assert calls == [0.5, 1.0]  # 0.5*2^0, 0.5*2^1

    def test_no_sleep_after_last_attempt(self):
        fn = MagicMock(side_effect=OSError())
        with patch("tilestitch.retry.time.sleep") as mock_sleep:
            with pytest.raises(RetryError):
                with_retry(fn, attempts=2, backoff=1.0, exceptions=(OSError,))
        assert mock_sleep.call_count == 1  # only between attempt 1 and 2


class TestWithRetryCallback:
    def test_on_retry_called_with_attempt_and_exception(self):
        exc = OSError("fail")
        fn = MagicMock(side_effect=[exc, b"ok"])
        callback = MagicMock()
        with patch("tilestitch.retry.time.sleep"):
            with_retry(fn, attempts=3, exceptions=(OSError,), on_retry=callback)
        callback.assert_called_once()
        call_args = callback.call_args
        assert call_args.args[0] == 1
        assert call_args.args[1] is exc
