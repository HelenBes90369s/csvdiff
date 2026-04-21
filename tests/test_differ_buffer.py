"""Tests for csvdiff.differ_buffer."""
import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_buffer import (
    BufferError,
    BufferOptions,
    BufferState,
    drain,
    flush,
    push,
)


def _change(key: str) -> RowChange:
    return RowChange(key=(key,), old_row={"id": key}, new_row={"id": key}, field_changes=[])


# ---------------------------------------------------------------------------
# BufferOptions
# ---------------------------------------------------------------------------

def test_options_default_valid():
    opts = BufferOptions()
    assert opts.max_size == 1000
    assert opts.overflow == "drop"


def test_options_zero_max_size_raises():
    with pytest.raises(BufferError, match="max_size"):
        BufferOptions(max_size=0)


def test_options_negative_max_size_raises():
    with pytest.raises(BufferError, match="max_size"):
        BufferOptions(max_size=-5)


def test_options_invalid_overflow_raises():
    with pytest.raises(BufferError, match="overflow"):
        BufferOptions(overflow="skip")


def test_options_raise_overflow_valid():
    opts = BufferOptions(overflow="raise")
    assert opts.overflow == "raise"


def test_options_flush_overflow_valid():
    opts = BufferOptions(overflow="flush")
    assert opts.overflow == "flush"


# ---------------------------------------------------------------------------
# push / flush / drain
# ---------------------------------------------------------------------------

def test_push_none_state_raises():
    with pytest.raises(BufferError):
        push(None, _change("a"))


def test_push_none_change_raises():
    state = BufferState(options=BufferOptions())
    with pytest.raises(BufferError):
        push(state, None)


def test_push_accepts_change():
    state = BufferState(options=BufferOptions(max_size=10))
    accepted = push(state, _change("a"))
    assert accepted is True
    assert state.size == 1


def test_push_drop_on_full():
    state = BufferState(options=BufferOptions(max_size=2, overflow="drop"))
    push(state, _change("a"))
    push(state, _change("b"))
    accepted = push(state, _change("c"))
    assert accepted is False
    assert state.size == 2


def test_push_raise_on_full():
    state = BufferState(options=BufferOptions(max_size=1, overflow="raise"))
    push(state, _change("a"))
    with pytest.raises(BufferError, match="full"):
        push(state, _change("b"))


def test_push_flush_on_full():
    state = BufferState(options=BufferOptions(max_size=2, overflow="flush"))
    push(state, _change("a"))
    push(state, _change("b"))
    # triggers flush, then appends
    accepted = push(state, _change("c"))
    assert accepted is True
    assert state.size == 1
    assert state.total_flushed == 2


def test_flush_none_state_raises():
    with pytest.raises(BufferError):
        flush(None)


def test_flush_clears_buffer():
    state = BufferState(options=BufferOptions())
    push(state, _change("x"))
    push(state, _change("y"))
    result = flush(state)
    assert isinstance(result, DiffResult)
    assert len(result.added) == 2
    assert state.size == 0
    assert state.total_flushed == 2


def test_drain_is_alias_for_flush():
    state = BufferState(options=BufferOptions())
    push(state, _change("z"))
    result = drain(state)
    assert len(result.added) == 1
    assert state.size == 0
