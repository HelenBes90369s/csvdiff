"""Tests for csvdiff.differ_hook."""
import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_hook import (
    HookError,
    HookOptions,
    HookState,
    run_hooks,
    run_with_hooks,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


# --- HookOptions ---

def test_hook_options_defaults_are_valid():
    opts = HookOptions()
    assert opts.before == []
    assert opts.after == []
    assert opts.on_error is None


def test_hook_options_before_not_list_raises():
    with pytest.raises(HookError):
        HookOptions(before="bad")  # type: ignore


def test_hook_options_after_not_list_raises():
    with pytest.raises(HookError):
        HookOptions(after=42)  # type: ignore


# --- run_hooks ---

def test_run_hooks_none_result_raises():
    opts = HookOptions()
    with pytest.raises(HookError):
        run_hooks(None, opts)  # type: ignore


def test_run_hooks_none_options_raises():
    with pytest.raises(HookError):
        run_hooks(_empty_result(), None)  # type: ignore


def test_run_hooks_invalid_phase_raises():
    with pytest.raises(HookError):
        run_hooks(_empty_result(), HookOptions(), phase="middle")


def test_run_hooks_after_calls_hooks():
    calls = []
    opts = HookOptions(after=[lambda r: calls.append(1), lambda r: calls.append(2)])
    state = run_hooks(_empty_result(), opts, phase="after")
    assert calls == [1, 2]
    assert state.after_calls == 2


def test_run_hooks_before_calls_hooks():
    calls = []
    opts = HookOptions(before=[lambda r: calls.append("b")])
    state = run_hooks(_empty_result(), opts, phase="before")
    assert calls == ["b"]
    assert state.before_calls == 1


def test_run_hooks_error_collected():
    def bad(r):
        raise ValueError("boom")

    errors = []
    opts = HookOptions(after=[bad], on_error=lambda e: errors.append(str(e)))
    state = run_hooks(_empty_result(), opts, phase="after")
    assert len(state.errors) == 1
    assert errors == ["boom"]


def test_run_hooks_error_without_handler():
    def bad(r):
        raise RuntimeError("oops")

    opts = HookOptions(after=[bad])
    state = run_hooks(_empty_result(), opts)
    assert len(state.errors) == 1


# --- run_with_hooks ---

def test_run_with_hooks_none_fn_raises():
    with pytest.raises(HookError):
        run_with_hooks(None, HookOptions())  # type: ignore


def test_run_with_hooks_none_options_raises():
    with pytest.raises(HookError):
        run_with_hooks(lambda: _empty_result(), None)  # type: ignore


def test_run_with_hooks_returns_result():
    r = _empty_result()
    out = run_with_hooks(lambda: r, HookOptions())
    assert out is r


def test_run_with_hooks_calls_before_and_after():
    log = []
    opts = HookOptions(
        before=[lambda r: log.append("before")],
        after=[lambda r: log.append("after")],
    )
    run_with_hooks(lambda: _empty_result(), opts)
    assert log == ["before", "after"]
