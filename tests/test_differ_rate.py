"""Tests for csvdiff.differ_rate."""
from __future__ import annotations

import time
import pytest

from csvdiff.differ import DiffResult
from csvdiff.differ_rate import (
    RateError,
    RateOptions,
    RateState,
    rate_limited,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


# ---------------------------------------------------------------------------
# RateOptions
# ---------------------------------------------------------------------------

def test_options_default_valid():
    opts = RateOptions()
    assert opts.max_calls == 10
    assert opts.window_seconds == 1.0


def test_options_zero_max_calls_raises():
    with pytest.raises(RateError, match="max_calls"):
        RateOptions(max_calls=0)


def test_options_negative_max_calls_raises():
    with pytest.raises(RateError, match="max_calls"):
        RateOptions(max_calls=-1)


def test_options_zero_window_raises():
    with pytest.raises(RateError, match="window_seconds"):
        RateOptions(window_seconds=0)


def test_options_negative_window_raises():
    with pytest.raises(RateError, match="window_seconds"):
        RateOptions(window_seconds=-0.5)


# ---------------------------------------------------------------------------
# RateState
# ---------------------------------------------------------------------------

def test_state_initially_allowed():
    state = RateState(options=RateOptions(max_calls=3, window_seconds=60))
    assert state.allowed() is True
    assert state.call_count == 0


def test_state_records_calls():
    state = RateState(options=RateOptions(max_calls=3, window_seconds=60))
    state.record()
    state.record()
    assert state.call_count == 2


def test_state_blocks_when_full():
    state = RateState(options=RateOptions(max_calls=2, window_seconds=60))
    state.record()
    state.record()
    assert state.allowed() is False


# ---------------------------------------------------------------------------
# rate_limited
# ---------------------------------------------------------------------------

def test_rate_limited_none_fn_raises():
    state = RateState(options=RateOptions())
    with pytest.raises(RateError, match="fn"):
        rate_limited(None, state)  # type: ignore[arg-type]


def test_rate_limited_none_state_raises():
    with pytest.raises(RateError, match="state"):
        rate_limited(_empty_result, None)  # type: ignore[arg-type]


def test_rate_limited_calls_fn():
    state = RateState(options=RateOptions(max_calls=5, window_seconds=60))
    result = rate_limited(_empty_result, state)
    assert isinstance(result, DiffResult)
    assert state.call_count == 1


def test_rate_limited_raises_when_exceeded():
    state = RateState(options=RateOptions(max_calls=2, window_seconds=60))
    rate_limited(_empty_result, state)
    rate_limited(_empty_result, state)
    with pytest.raises(RateError, match="Rate limit exceeded"):
        rate_limited(_empty_result, state)


def test_rate_limited_resets_after_window(monkeypatch):
    """Calls older than the window should not count."""
    state = RateState(options=RateOptions(max_calls=1, window_seconds=0.05))
    rate_limited(_empty_result, state)
    time.sleep(0.1)
    # window has passed; should be allowed again
    result = rate_limited(_empty_result, state)
    assert isinstance(result, DiffResult)
