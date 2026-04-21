"""Tests for csvdiff.differ_semaphore."""
from __future__ import annotations

import threading
import time

import pytest

from csvdiff.differ import DiffResult
from csvdiff.differ_semaphore import (
    SemaphoreError,
    SemaphoreOptions,
    SemaphoreState,
    make_semaphore,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


# ---------------------------------------------------------------------------
# SemaphoreOptions validation
# ---------------------------------------------------------------------------

def test_options_default_valid():
    opts = SemaphoreOptions()
    assert opts.max_concurrent == 4
    assert opts.timeout is None


def test_options_zero_max_concurrent_raises():
    with pytest.raises(SemaphoreError, match="max_concurrent"):
        SemaphoreOptions(max_concurrent=0)


def test_options_negative_max_concurrent_raises():
    with pytest.raises(SemaphoreError, match="max_concurrent"):
        SemaphoreOptions(max_concurrent=-1)


def test_options_zero_timeout_raises():
    with pytest.raises(SemaphoreError, match="timeout"):
        SemaphoreOptions(timeout=0.0)


def test_options_negative_timeout_raises():
    with pytest.raises(SemaphoreError, match="timeout"):
        SemaphoreOptions(timeout=-5.0)


def test_options_positive_timeout_valid():
    opts = SemaphoreOptions(timeout=2.5)
    assert opts.timeout == 2.5


# ---------------------------------------------------------------------------
# make_semaphore
# ---------------------------------------------------------------------------

def test_make_semaphore_returns_state():
    state = make_semaphore()
    assert isinstance(state, SemaphoreState)
    assert state.active == 0


def test_make_semaphore_with_options():
    opts = SemaphoreOptions(max_concurrent=2)
    state = make_semaphore(opts)
    assert state.options.max_concurrent == 2


# ---------------------------------------------------------------------------
# SemaphoreState.run
# ---------------------------------------------------------------------------

def test_run_returns_result():
    state = make_semaphore()
    result = state.run(_empty_result)
    assert isinstance(result, DiffResult)


def test_active_count_zero_after_run():
    state = make_semaphore()
    state.run(_empty_result)
    assert state.active == 0


def test_active_count_increments_during_run():
    state = make_semaphore(SemaphoreOptions(max_concurrent=2))
    snapshots: list[int] = []

    def slow_fn() -> DiffResult:
        snapshots.append(state.active)
        time.sleep(0.05)
        return _empty_result()

    t = threading.Thread(target=state.run, args=(slow_fn,))
    t.start()
    time.sleep(0.01)
    snapshots.append(state.active)  # captured mid-flight
    t.join()
    assert 1 in snapshots


def test_semaphore_blocks_excess_concurrent():
    """With max_concurrent=1 and timeout=0.1, a second call should time out."""
    state = make_semaphore(SemaphoreOptions(max_concurrent=1, timeout=0.1))
    barrier = threading.Barrier(2)
    errors: list[Exception] = []

    def hold() -> DiffResult:
        barrier.wait()       # both threads reach this point
        time.sleep(0.3)      # hold the semaphore
        return _empty_result()

    def try_acquire() -> None:
        try:
            barrier.wait()   # sync with hold()
            state.run(_empty_result)
        except SemaphoreError as exc:
            errors.append(exc)

    t1 = threading.Thread(target=state.run, args=(hold,))
    t2 = threading.Thread(target=try_acquire)
    t1.start()
    t2.start()
    t1.join(timeout=2)
    t2.join(timeout=2)
    assert len(errors) == 1
    assert "semaphore" in str(errors[0]).lower()
