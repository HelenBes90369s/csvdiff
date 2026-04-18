"""Tests for csvdiff.differ_batch."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult
from csvdiff.differ_batch import (
    BatchError,
    BatchOptions,
    BatchResult,
    run_batch,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _ok_fn(a: str, b: str) -> DiffResult:
    return _empty_result()


def _fail_fn(a: str, b: str) -> DiffResult:
    raise ValueError(f"simulated failure: {a}")


# --- options ---

def test_batch_options_default_valid():
    opts = BatchOptions()
    assert opts.stop_on_error is False
    assert opts.label_pairs is True


# --- run_batch basic ---

def test_run_batch_none_pairs_raises():
    with pytest.raises(BatchError):
        run_batch(None, _ok_fn)


def test_run_batch_none_fn_raises():
    with pytest.raises(BatchError):
        run_batch([], None)


def test_run_batch_empty_pairs_returns_empty():
    result = run_batch([], _ok_fn)
    assert isinstance(result, BatchResult)
    assert result.entries == []
    assert result.all_ok is True


def test_run_batch_single_ok_pair():
    result = run_batch([("a.csv", "b.csv")], _ok_fn)
    assert len(result.entries) == 1
    assert result.entries[0].ok
    assert result.entries[0].label == "a.csv vs b.csv"
    assert result.entries[0].result is not None
    assert result.entries[0].error is None


def test_run_batch_multiple_ok_pairs():
    pairs = [("a.csv", "b.csv"), ("c.csv", "d.csv")]
    result = run_batch(pairs, _ok_fn)
    assert len(result.entries) == 2
    assert result.all_ok
    assert len(result.succeeded) == 2
    assert len(result.failed) == 0


def test_run_batch_error_recorded_without_stop():
    pairs = [("a.csv", "b.csv"), ("c.csv", "d.csv")]
    result = run_batch(pairs, _fail_fn, BatchOptions(stop_on_error=False))
    assert len(result.entries) == 2
    assert not result.all_ok
    assert len(result.failed) == 2
    assert "simulated failure" in result.failed[0].error


def test_run_batch_stop_on_error_raises():
    pairs = [("a.csv", "b.csv"), ("c.csv", "d.csv")]
    with pytest.raises(BatchError, match="Batch stopped"):
        run_batch(pairs, _fail_fn, BatchOptions(stop_on_error=True))


def test_run_batch_label_pairs_false_uses_index():
    result = run_batch([("x.csv", "y.csv")], _ok_fn, BatchOptions(label_pairs=False))
    assert result.entries[0].label == "0"


def test_run_batch_mixed_ok_and_fail():
    calls = [0]

    def mixed_fn(a: str, b: str) -> DiffResult:
        calls[0] += 1
        if calls[0] == 2:
            raise RuntimeError("boom")
        return _empty_result()

    pairs = [("a", "b"), ("c", "d"), ("e", "f")]
    result = run_batch(pairs, mixed_fn)
    assert len(result.succeeded) == 2
    assert len(result.failed) == 1
    assert result.failed[0].label == "c vs d"
