"""Tests for csvdiff.differ_throttle_burst."""
from __future__ import annotations

import time

import pytest

from csvdiff.differ import DiffResult
from csvdiff.differ_throttle_burst import (
    BurstThrottleError,
    BurstThrottleOptions,
    BurstThrottleState,
    throttle_burst,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


# ---------------------------------------------------------------------------
# Options validation
# ---------------------------------------------------------------------------

def test_options_default_valid() -> None:
    opts = BurstThrottleOptions()
    assert opts.burst_size == 5
    assert opts.rate_per_second == 1.0
    assert opts.raise_on_exceed is False


def test_options_zero_burst_raises() -> None:
    with pytest.raises(BurstThrottleError, match="burst_size"):
        BurstThrottleOptions(burst_size=0)


def test_options_negative_burst_raises() -> None:
    with pytest.raises(BurstThrottleError, match="burst_size"):
        BurstThrottleOptions(burst_size=-1)


def test_options_zero_rate_raises() -> None:
    with pytest.raises(BurstThrottleError, match="rate_per_second"):
        BurstThrottleOptions(rate_per_second=0.0)


def test_options_negative_rate_raises() -> None:
    with pytest.raises(BurstThrottleError, match="rate_per_second"):
        BurstThrottleOptions(rate_per_second=-2.0)


# ---------------------------------------------------------------------------
# State behaviour
# ---------------------------------------------------------------------------

def test_state_initial_tokens_equal_burst_size() -> None:
    opts = BurstThrottleOptions(burst_size=3, rate_per_second=1.0)
    state = BurstThrottleState(opts)
    assert state._tokens == 3.0


def test_state_burst_allows_n_calls_immediately() -> None:
    opts = BurstThrottleOptions(burst_size=4, rate_per_second=100.0)
    state = BurstThrottleState(opts)
    results = [state.allowed() for _ in range(4)]
    assert all(results)
    assert state.call_count == 4


def test_state_burst_exceeded_returns_false() -> None:
    opts = BurstThrottleOptions(burst_size=2, rate_per_second=0.01)
    state = BurstThrottleState(opts)
    state.allowed()  # 1
    state.allowed()  # 2
    assert state.allowed() is False  # burst exhausted, refill is negligible


def test_state_tokens_refill_over_time() -> None:
    opts = BurstThrottleOptions(burst_size=1, rate_per_second=50.0)
    state = BurstThrottleState(opts)
    state.allowed()  # consume the single token
    time.sleep(0.05)  # ~2.5 tokens at 50/s
    assert state.allowed() is True


# ---------------------------------------------------------------------------
# throttle_burst integration
# ---------------------------------------------------------------------------

def test_throttle_burst_calls_fn_and_returns_result() -> None:
    opts = BurstThrottleOptions(burst_size=5, rate_per_second=100.0)
    state = BurstThrottleState(opts)
    result = throttle_burst(_empty_result, state)
    assert isinstance(result, DiffResult)


def test_throttle_burst_raise_on_exceed_raises_when_exhausted() -> None:
    opts = BurstThrottleOptions(burst_size=1, rate_per_second=0.01, raise_on_exceed=True)
    state = BurstThrottleState(opts)
    throttle_burst(_empty_result, state)  # first call uses the burst token
    with pytest.raises(BurstThrottleError, match="exceeded"):
        throttle_burst(_empty_result, state)


def test_throttle_burst_increments_call_count() -> None:
    opts = BurstThrottleOptions(burst_size=10, rate_per_second=100.0)
    state = BurstThrottleState(opts)
    for _ in range(5):
        throttle_burst(_empty_result, state)
    assert state.call_count == 5
