"""Tests for csvdiff.differ_throttle."""
import time
import pytest

from csvdiff.differ import DiffResult
from csvdiff.differ_throttle import (
    ThrottleError,
    ThrottleOptions,
    ThrottleState,
    throttled_run,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


# --- ThrottleOptions ---

def test_options_default_valid():
    o = ThrottleOptions()
    assert o.min_interval == 1.0
    assert o.max_calls == 0
    assert o.raise_on_limit is False


def test_options_zero_interval_raises():
    with pytest.raises(ThrottleError):
        ThrottleOptions(min_interval=0)


def test_options_negative_interval_raises():
    with pytest.raises(ThrottleError):
        ThrottleOptions(min_interval=-0.5)


def test_options_negative_max_calls_raises():
    with pytest.raises(ThrottleError):
        ThrottleOptions(max_calls=-1)


# --- ThrottleState ---

def test_state_ready_initially():
    state = ThrottleState(ThrottleOptions(min_interval=0.01))
    assert state.ready()


def test_state_not_ready_immediately_after_record():
    state = ThrottleState(ThrottleOptions(min_interval=10.0))
    state.record()
    assert not state.ready()


def test_state_call_count_increments():
    state = ThrottleState(ThrottleOptions(min_interval=0.01))
    state.record()
    state.record()
    assert state.call_count == 2


def test_state_max_calls_blocks_ready():
    state = ThrottleState(ThrottleOptions(min_interval=0.01, max_calls=1))
    state.record()
    assert not state.ready()


# --- throttled_run ---

def test_throttled_run_returns_result():
    state = ThrottleState(ThrottleOptions(min_interval=0.01))
    result = throttled_run(_empty_result, state)
    assert result is not None
    assert state.call_count == 1


def test_throttled_run_respects_interval():
    state = ThrottleState(ThrottleOptions(min_interval=0.05))
    t0 = time.monotonic()
    throttled_run(_empty_result, state)
    throttled_run(_empty_result, state)
    elapsed = time.monotonic() - t0
    assert elapsed >= 0.05


def test_throttled_run_returns_none_at_limit():
    state = ThrottleState(ThrottleOptions(min_interval=0.01, max_calls=1))
    throttled_run(_empty_result, state)
    result = throttled_run(_empty_result, state)
    assert result is None
    assert state.call_count == 1


def test_throttled_run_raises_at_limit_when_configured():
    state = ThrottleState(
        ThrottleOptions(min_interval=0.01, max_calls=1, raise_on_limit=True)
    )
    throttled_run(_empty_result, state)
    with pytest.raises(ThrottleError, match="call limit"):
        throttled_run(_empty_result, state)
