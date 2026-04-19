"""Tests for csvdiff.differ_debounce."""
import pytest

from csvdiff.differ import DiffResult
from csvdiff.differ_debounce import (
    DebounceError,
    DebounceOptions,
    DebounceState,
    debounce_diff,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


# --- DebounceOptions ---

def test_options_default_valid():
    o = DebounceOptions()
    assert o.window == 1.0
    assert o.max_wait == 0.0


def test_options_zero_window_raises():
    with pytest.raises(DebounceError, match="window"):
        DebounceOptions(window=0)


def test_options_negative_window_raises():
    with pytest.raises(DebounceError, match="window"):
        DebounceOptions(window=-0.5)


def test_options_negative_max_wait_raises():
    with pytest.raises(DebounceError, match="max_wait"):
        DebounceOptions(max_wait=-1.0)


def test_options_max_wait_less_than_window_raises():
    with pytest.raises(DebounceError, match="max_wait"):
        DebounceOptions(window=2.0, max_wait=1.0)


def test_options_max_wait_equal_to_window_ok():
    o = DebounceOptions(window=1.0, max_wait=1.0)
    assert o.max_wait == 1.0


# --- DebounceState.should_fire ---

def test_should_fire_false_when_no_pending():
    state = DebounceState(DebounceOptions(window=0.5))
    assert not state.should_fire(now=100.0)


def test_should_fire_false_within_window():
    state = DebounceState(DebounceOptions(window=1.0))
    state.record_call(now=100.0)
    assert not state.should_fire(now=100.5)


def test_should_fire_true_after_window():
    state = DebounceState(DebounceOptions(window=1.0))
    state.record_call(now=100.0)
    assert state.should_fire(now=101.1)


def test_should_fire_true_after_max_wait():
    state = DebounceState(DebounceOptions(window=1.0, max_wait=3.0))
    state.record_call(now=100.0)
    state.record_call(now=100.5)
    state.record_call(now=101.0)
    # within window but max_wait exceeded
    assert state.should_fire(now=103.1)


# --- DebounceState.fire ---

def test_fire_returns_result_and_clears_pending():
    state = DebounceState(DebounceOptions(window=0.5))
    state.record_call(now=100.0)
    result = state.fire(fn=_empty_result, now=100.6)
    assert isinstance(result, DiffResult)
    assert not state._pending


def test_fire_stores_last_result():
    state = DebounceState(DebounceOptions(window=0.5))
    state.record_call(now=100.0)
    state.fire(fn=_empty_result, now=100.6)
    assert state._last_result is not None


# --- debounce_diff factory ---

def test_debounce_diff_returns_state():
    state = debounce_diff(fn=_empty_result)
    assert isinstance(state, DebounceState)


def test_debounce_diff_custom_options():
    opts = DebounceOptions(window=2.0)
    state = debounce_diff(fn=_empty_result, options=opts)
    assert state.options.window == 2.0
