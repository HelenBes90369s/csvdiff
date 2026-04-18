"""Tests for csvdiff.differ_timeout."""
import time
import pytest

from csvdiff.differ import DiffResult
from csvdiff.differ_timeout import (
    TimeoutError,
    TimeoutOptions,
    run_with_timeout,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


# ---------------------------------------------------------------------------
# TimeoutOptions
# ---------------------------------------------------------------------------

def test_timeout_options_default_valid():
    opts = TimeoutOptions()
    assert opts.seconds == 30


def test_timeout_options_zero_raises():
    with pytest.raises(ValueError, match="seconds"):
        TimeoutOptions(seconds=0)


def test_timeout_options_negative_raises():
    with pytest.raises(ValueError, match="seconds"):
        TimeoutOptions(seconds=-5)


def test_timeout_options_blank_message_raises():
    with pytest.raises(ValueError, match="message"):
        TimeoutOptions(message="   ")


# ---------------------------------------------------------------------------
# run_with_timeout
# ---------------------------------------------------------------------------

def test_run_with_timeout_returns_result():
    result = run_with_timeout(_empty_result, TimeoutOptions(seconds=5))
    assert isinstance(result, DiffResult)
    assert result.added == []


def test_run_with_timeout_none_fn_raises():
    with pytest.raises(TimeoutError):
        run_with_timeout(None, TimeoutOptions(seconds=5))  # type: ignore[arg-type]


def test_run_with_timeout_uses_default_options():
    result = run_with_timeout(_empty_result)
    assert result.removed == []


def test_run_with_timeout_exceeds_limit():
    opts = TimeoutOptions(seconds=1, message="too slow")

    def slow() -> DiffResult:  # pragma: no cover
        time.sleep(5)
        return _empty_result()

    with pytest.raises(TimeoutError, match="too slow"):
        run_with_timeout(slow, opts)
