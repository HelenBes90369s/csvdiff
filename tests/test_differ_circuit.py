"""Tests for csvdiff.differ_circuit."""
from __future__ import annotations

import time
import pytest

from csvdiff.differ import DiffResult
from csvdiff.differ_circuit import (
    CircuitError,
    CircuitOptions,
    CircuitState,
    run_with_circuit,
    _STATE_CLOSED,
    _STATE_OPEN,
    _STATE_HALF_OPEN,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


# ---------------------------------------------------------------------------
# CircuitOptions validation
# ---------------------------------------------------------------------------

def test_options_default_valid():
    opts = CircuitOptions()
    assert opts.threshold == 3
    assert opts.reset_timeout == 60.0
    assert opts.half_open_calls == 1


def test_options_zero_threshold_raises():
    with pytest.raises(CircuitError, match="threshold"):
        CircuitOptions(threshold=0)


def test_options_negative_reset_timeout_raises():
    with pytest.raises(CircuitError, match="reset_timeout"):
        CircuitOptions(reset_timeout=-1.0)


def test_options_zero_reset_timeout_raises():
    with pytest.raises(CircuitError, match="reset_timeout"):
        CircuitOptions(reset_timeout=0.0)


def test_options_zero_half_open_calls_raises():
    with pytest.raises(CircuitError, match="half_open_calls"):
        CircuitOptions(half_open_calls=0)


# ---------------------------------------------------------------------------
# CircuitState transitions
# ---------------------------------------------------------------------------

def test_initial_state_is_closed():
    state = CircuitState(CircuitOptions(threshold=2))
    assert state.state == _STATE_CLOSED


def test_failures_below_threshold_stay_closed():
    state = CircuitState(CircuitOptions(threshold=3))
    state.record_failure()
    state.record_failure()
    assert state.state == _STATE_CLOSED


def test_failures_at_threshold_open_circuit():
    state = CircuitState(CircuitOptions(threshold=2))
    state.record_failure()
    state.record_failure()
    assert state.state == _STATE_OPEN


def test_success_resets_failure_count():
    state = CircuitState(CircuitOptions(threshold=3))
    state.record_failure()
    state.record_failure()
    state.record_success()
    state.record_failure()  # only 1 failure now
    assert state.state == _STATE_CLOSED


def test_open_circuit_transitions_to_half_open_after_timeout():
    opts = CircuitOptions(threshold=1, reset_timeout=0.05)
    state = CircuitState(opts)
    state.record_failure()  # opens circuit
    assert state.state == _STATE_OPEN
    time.sleep(0.06)
    assert state.state == _STATE_HALF_OPEN


def test_half_open_success_closes_circuit():
    opts = CircuitOptions(threshold=1, reset_timeout=0.05, half_open_calls=1)
    state = CircuitState(opts)
    state.record_failure()
    time.sleep(0.06)
    assert state.state == _STATE_HALF_OPEN
    state.record_success()
    assert state.state == _STATE_CLOSED


# ---------------------------------------------------------------------------
# run_with_circuit
# ---------------------------------------------------------------------------

def test_run_with_circuit_success_returns_result():
    state = CircuitState(CircuitOptions())
    result = run_with_circuit(_empty_result, state)
    assert isinstance(result, DiffResult)


def test_run_with_circuit_open_raises():
    opts = CircuitOptions(threshold=1, reset_timeout=60.0)
    state = CircuitState(opts)
    state.record_failure()  # open the circuit manually
    with pytest.raises(CircuitError, match="open"):
        run_with_circuit(_empty_result, state)


def test_run_with_circuit_propagates_exception_and_records_failure():
    state = CircuitState(CircuitOptions(threshold=2))

    def boom() -> DiffResult:
        raise ValueError("exploded")

    with pytest.raises(ValueError):
        run_with_circuit(boom, state)
    assert state._failures == 1


def test_run_with_circuit_opens_after_threshold_failures():
    opts = CircuitOptions(threshold=2)
    state = CircuitState(opts)

    def boom() -> DiffResult:
        raise RuntimeError("fail")

    for _ in range(2):
        with pytest.raises(RuntimeError):
            run_with_circuit(boom, state)

    with pytest.raises(CircuitError, match="open"):
        run_with_circuit(_empty_result, state)
