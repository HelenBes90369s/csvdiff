"""Tests for csvdiff.differ_pool."""
import pytest

from csvdiff.differ import DiffResult
from csvdiff.differ_queue import QueueEntry
from csvdiff.differ_pool import (
    PoolError,
    PoolOptions,
    PoolResult,
    run_pool,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _entry(job_id: str) -> QueueEntry:
    return QueueEntry(job_id=job_id, result=_empty_result())


def _identity(entry: QueueEntry) -> DiffResult:
    return entry.result


def _boom(entry: QueueEntry) -> DiffResult:
    raise ValueError(f"exploded on {entry.job_id}")


# ---------------------------------------------------------------------------
# PoolOptions validation
# ---------------------------------------------------------------------------

def test_options_default_valid():
    opts = PoolOptions()
    assert opts.workers == 2
    assert opts.timeout == 30.0
    assert opts.reraise is False


def test_options_zero_workers_raises():
    with pytest.raises(PoolError, match="workers"):
        PoolOptions(workers=0)


def test_options_negative_timeout_raises():
    with pytest.raises(PoolError, match="timeout"):
        PoolOptions(timeout=-1.0)


def test_options_zero_timeout_raises():
    with pytest.raises(PoolError, match="timeout"):
        PoolOptions(timeout=0)


# ---------------------------------------------------------------------------
# run_pool basics
# ---------------------------------------------------------------------------

def test_run_pool_none_entries_raises():
    with pytest.raises(PoolError):
        run_pool(None, _identity)


def test_run_pool_non_callable_fn_raises():
    with pytest.raises(PoolError, match="callable"):
        run_pool([], "not_a_fn")


def test_run_pool_empty_entries_returns_empty():
    results = run_pool([], _identity)
    assert results == []


def test_run_pool_single_entry():
    entries = [_entry("a")]
    results = run_pool(entries, _identity)
    assert len(results) == 1
    assert results[0].job_id == "a"
    assert results[0].ok()


def test_run_pool_multiple_entries_ordered():
    entries = [_entry(str(i)) for i in range(5)]
    results = run_pool(entries, _identity, PoolOptions(workers=3))
    assert [r.job_id for r in results] == [str(i) for i in range(5)]


# ---------------------------------------------------------------------------
# error handling
# ---------------------------------------------------------------------------

def test_run_pool_error_captured_when_not_reraise():
    entries = [_entry("bad")]
    results = run_pool(entries, _boom, PoolOptions(reraise=False))
    assert len(results) == 1
    assert not results[0].ok()
    assert "exploded" in results[0].error


def test_run_pool_error_reraised_when_reraise_true():
    entries = [_entry("bad")]
    with pytest.raises(PoolError, match="failed"):
        run_pool(entries, _boom, PoolOptions(reraise=True))


# ---------------------------------------------------------------------------
# PoolResult.ok
# ---------------------------------------------------------------------------

def test_pool_result_ok_no_error():
    pr = PoolResult(job_id="x", result=_empty_result())
    assert pr.ok() is True


def test_pool_result_ok_with_error():
    pr = PoolResult(job_id="x", result=_empty_result(), error="oops")
    assert pr.ok() is False
