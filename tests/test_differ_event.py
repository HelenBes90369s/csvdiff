"""Tests for csvdiff.differ_event."""
import pytest
from csvdiff.differ import DiffResult
from csvdiff.differ_event import (
    EventError, EventOptions, EventState, emit, run_with_events,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def test_options_default_valid():
    opts = EventOptions()
    assert opts.listeners == {}


def test_options_unknown_event_raises():
    with pytest.raises(EventError, match="Unknown event"):
        EventOptions(listeners={"bad_event": []})


def test_options_non_list_listeners_raises():
    with pytest.raises(EventError, match="must be a list"):
        EventOptions(listeners={"before_diff": lambda x: x})  # type: ignore


def test_options_non_callable_raises():
    with pytest.raises(EventError, match="callable"):
        EventOptions(listeners={"after_diff": ["not_callable"]})


def test_emit_unknown_event_raises():
    opts = EventOptions()
    with pytest.raises(EventError, match="Unknown event"):
        emit(opts, "mystery", None)


def test_emit_calls_listener():
    received = []
    opts = EventOptions(listeners={"before_diff": [lambda p: received.append(p)]})
    emit(opts, "before_diff", "hello")
    assert received == ["hello"]


def test_emit_records_to_state():
    state = EventState()
    opts = EventOptions()
    emit(opts, "after_diff", "payload", state)
    assert state.emitted == [("after_diff", "payload")]


def test_emit_multiple_listeners():
    log = []
    opts = EventOptions(listeners={"on_error": [
        lambda p: log.append(("a", p)),
        lambda p: log.append(("b", p)),
    ]})
    emit(opts, "on_error", "err")
    assert log == [("a", "err"), ("b", "err")]


def test_run_with_events_none_fn_raises():
    opts = EventOptions()
    with pytest.raises(EventError, match="fn must not be None"):
        run_with_events(None, opts)  # type: ignore


def test_run_with_events_returns_result():
    opts = EventOptions()
    result = run_with_events(_empty_result, opts)
    assert isinstance(result, DiffResult)


def test_run_with_events_fires_before_and_after():
    log = []
    opts = EventOptions(listeners={
        "before_diff": [lambda p: log.append("before")],
        "after_diff": [lambda p: log.append("after")],
    })
    run_with_events(_empty_result, opts)
    assert log == ["before", "after"]


def test_run_with_events_fires_on_error():
    errors = []
    opts = EventOptions(listeners={"on_error": [lambda p: errors.append(p)]})

    def boom() -> DiffResult:
        raise ValueError("oops")

    with pytest.raises(ValueError):
        run_with_events(boom, opts)
    assert len(errors) == 1 and isinstance(errors[0], ValueError)


def test_run_with_events_state_records_events():
    state = EventState()
    opts = EventOptions()
    run_with_events(_empty_result, opts, state)
    names = [e[0] for e in state.emitted]
    assert "before_diff" in names and "after_diff" in names
