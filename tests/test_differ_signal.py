"""Tests for csvdiff.differ_signal."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.differ_signal import (
    SignalError,
    SignalOptions,
    SignalState,
    emit_diff_signals,
    KNOWN_SIGNALS,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _fc(field: str = "col", old: str = "a", new: str = "b") -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key=("k",), changes=None):
    return RowChange(
        key=key,
        old_row={"id": key[0]},
        new_row={"id": key[0]},
        changes=changes or [_fc()],
    )


def make_result(added=None, removed=None, changed=None):
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


# ---------------------------------------------------------------------------
# SignalOptions validation
# ---------------------------------------------------------------------------

def test_options_default_valid():
    opts = SignalOptions()
    assert opts.handlers == {}
    assert opts.stop_on_error is False


def test_options_unknown_signal_raises():
    with pytest.raises(SignalError, match="Unknown signals"):
        SignalOptions(handlers={"bad_signal": []})


def test_options_non_list_handlers_raises():
    with pytest.raises(SignalError, match="must be a list"):
        SignalOptions(handlers={"post_diff": lambda r: r})  # type: ignore


def test_options_non_callable_handler_raises():
    with pytest.raises(SignalError, match="must be callable"):
        SignalOptions(handlers={"post_diff": ["not_a_function"]})


def test_options_valid_known_signals():
    for sig in KNOWN_SIGNALS:
        opts = SignalOptions(handlers={sig: [lambda x: x]})
        assert sig in opts.handlers


# ---------------------------------------------------------------------------
# SignalState.fire
# ---------------------------------------------------------------------------

def test_fire_unknown_signal_raises():
    state = SignalState(options=SignalOptions())
    with pytest.raises(SignalError, match="Unknown signal"):
        state.fire("nonexistent")


def test_fire_calls_handler():
    calls = []
    opts = SignalOptions(handlers={"post_diff": [lambda p: calls.append(p)]})
    state = SignalState(options=opts)
    result = make_result()
    state.fire("post_diff", result)
    assert calls == [result]


def test_fire_collects_return_values():
    opts = SignalOptions(handlers={"on_empty": [lambda p: 42, lambda p: 99]})
    state = SignalState(options=opts)
    state.fire("on_empty", None)
    assert state.fired("on_empty") == [42, 99]


def test_fire_handler_error_ignored_by_default():
    def boom(p):
        raise RuntimeError("oops")

    opts = SignalOptions(handlers={"on_error": [boom]})
    state = SignalState(options=opts)
    # should not raise
    state.fire("on_error", Exception("e"))


def test_fire_handler_error_raised_when_stop_on_error():
    def boom(p):
        raise RuntimeError("oops")

    opts = SignalOptions(
        handlers={"on_error": [boom]}, stop_on_error=True
    )
    state = SignalState(options=opts)
    with pytest.raises(SignalError, match="oops"):
        state.fire("on_error", Exception("e"))


# ---------------------------------------------------------------------------
# emit_diff_signals
# ---------------------------------------------------------------------------

def test_emit_none_state_raises():
    with pytest.raises(SignalError, match="None"):
        emit_diff_signals(None, make_result())  # type: ignore


def test_emit_fires_post_diff():
    calls = []
    opts = SignalOptions(handlers={"post_diff": [lambda p: calls.append("post")]})
    state = SignalState(options=opts)
    result = make_result()
    emit_diff_signals(state, result)
    assert calls == ["post"]


def test_emit_fires_on_empty_when_no_changes():
    calls = []
    opts = SignalOptions(handlers={"on_empty": [lambda p: calls.append("empty")]})
    state = SignalState(options=opts)
    emit_diff_signals(state, make_result())
    assert calls == ["empty"]


def test_emit_fires_on_changed_when_changes_present():
    calls = []
    opts = SignalOptions(
        handlers={"on_changed": [lambda p: calls.append("changed")]}
    )
    state = SignalState(options=opts)
    result = make_result(changed=[_change()])
    emit_diff_signals(state, result)
    assert calls == ["changed"]


def test_emit_fires_on_error_and_skips_others():
    post_calls = []
    err_calls = []
    opts = SignalOptions(
        handlers={
            "post_diff": [lambda p: post_calls.append(p)],
            "on_error": [lambda p: err_calls.append(p)],
        }
    )
    state = SignalState(options=opts)
    exc = ValueError("bad")
    emit_diff_signals(state, make_result(), error=exc)
    assert err_calls == [exc]
    assert post_calls == []


def test_emit_returns_result_unchanged():
    opts = SignalOptions()
    state = SignalState(options=opts)
    result = make_result(added=[{"id": "1"}])
    returned = emit_diff_signals(state, result)
    assert returned is result
