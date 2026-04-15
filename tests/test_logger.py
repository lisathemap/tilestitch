"""Tests for tilestitch.logger."""

import io
import logging

import pytest

from tilestitch.logger import (
    LOGGER_NAME,
    configure_logging,
    get_logger,
    set_level,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_logger():
    """Return the tilestitch root logger with all handlers removed."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.handlers.clear()
    return logger


# ---------------------------------------------------------------------------
# get_logger
# ---------------------------------------------------------------------------

class TestGetLogger:
    def test_returns_logger_instance(self):
        assert isinstance(get_logger(), logging.Logger)

    def test_root_logger_name(self):
        assert get_logger().name == LOGGER_NAME

    def test_child_logger_name(self):
        child = get_logger("stitcher")
        assert child.name == f"{LOGGER_NAME}.stitcher"

    def test_different_names_return_different_loggers(self):
        assert get_logger("a") is not get_logger("b")

    def test_same_name_returns_same_instance(self):
        assert get_logger("x") is get_logger("x")


# ---------------------------------------------------------------------------
# configure_logging
# ---------------------------------------------------------------------------

class TestConfigureLogging:
    def test_sets_info_level_by_default(self):
        logger = _fresh_logger()
        configure_logging(stream=io.StringIO())
        assert logger.level == logging.INFO

    def test_sets_debug_level(self):
        logger = _fresh_logger()
        configure_logging(level="debug", stream=io.StringIO())
        assert logger.level == logging.DEBUG

    def test_sets_warning_level(self):
        logger = _fresh_logger()
        configure_logging(level="warning", stream=io.StringIO())
        assert logger.level == logging.WARNING

    def test_handler_writes_to_provided_stream(self):
        stream = io.StringIO()
        _fresh_logger()
        configure_logging(level="debug", stream=stream)
        get_logger().debug("hello stream")
        assert "hello stream" in stream.getvalue()

    def test_does_not_duplicate_handlers_on_reconfigure(self):
        logger = _fresh_logger()
        stream = io.StringIO()
        configure_logging(stream=stream)
        configure_logging(stream=stream)
        assert len(logger.handlers) == 1

    def test_custom_format_applied(self):
        stream = io.StringIO()
        _fresh_logger()
        configure_logging(fmt="CUSTOM %(message)s", stream=stream)
        get_logger().info("msg")
        assert "CUSTOM msg" in stream.getvalue()


# ---------------------------------------------------------------------------
# set_level
# ---------------------------------------------------------------------------

class TestSetLevel:
    def test_changes_level_to_error(self):
        _fresh_logger()
        configure_logging(stream=io.StringIO())
        set_level("error")
        assert logging.getLogger(LOGGER_NAME).level == logging.ERROR

    def test_invalid_level_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid log level"):
            set_level("verbose")

    def test_case_insensitive(self):
        _fresh_logger()
        configure_logging(stream=io.StringIO())
        set_level("DEBUG")
        assert logging.getLogger(LOGGER_NAME).level == logging.DEBUG
