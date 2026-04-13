"""Tests for csvdiff.truncator."""

from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.truncator import (
    TruncateError,
    TruncateOptions,
    truncate_diff,
)


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def make_change(key: tuple, kind: str = "changed") -> RowChange:
    return RowChange(
        key=key,
        kind=kind,
        row={"id": key[0]},
        changes=[_fc("name", "a", "b")] if kind == "changed" else [],
    )


def make_result(n_added: int = 0, n_removed: int = 0, n_changed: int = 0) -> DiffResult:
    return DiffResult(
        added=[make_change((str(i),), "added") for i in range(n_added)],
        removed=[make_change((str(i),), "removed") for i in range(n_removed)],
        changed=[make_change((str(i),), "changed") for i in range(n_changed)],
    )


def test_truncate_options_negative_raises():
    with pytest.raises(TruncateError):
        TruncateOptions(max_added=-1)


def test_truncate_options_zero_is_valid():
    opts = TruncateOptions(max_added=0, max_removed=0, max_changed=0)
    assert opts.max_added == 0


def test_no_truncation_when_limits_none():
    result = make_result(n_added=5, n_removed=3, n_changed=4)
    tr = truncate_diff(result, TruncateOptions())
    assert len(tr.diff.added) == 5
    assert len(tr.diff.removed) == 3
    assert len(tr.diff.changed) == 4
    assert not tr.any_truncated


def test_truncate_added():
    result = make_result(n_added=10)
    tr = truncate_diff(result, TruncateOptions(max_added=3))
    assert len(tr.diff.added) == 3
    assert tr.added_truncated is True
    assert tr.removed_truncated is False
    assert tr.changed_truncated is False


def test_truncate_removed():
    result = make_result(n_removed=7)
    tr = truncate_diff(result, TruncateOptions(max_removed=2))
    assert len(tr.diff.removed) == 2
    assert tr.removed_truncated is True


def test_truncate_changed():
    result = make_result(n_changed=8)
    tr = truncate_diff(result, TruncateOptions(max_changed=5))
    assert len(tr.diff.changed) == 5
    assert tr.changed_truncated is True


def test_no_truncation_when_under_limit():
    result = make_result(n_added=2, n_removed=2, n_changed=2)
    tr = truncate_diff(result, TruncateOptions(max_added=10, max_removed=10, max_changed=10))
    assert not tr.any_truncated


def test_truncate_to_zero():
    result = make_result(n_added=5, n_removed=5, n_changed=5)
    tr = truncate_diff(result, TruncateOptions(max_added=0, max_removed=0, max_changed=0))
    assert len(tr.diff.added) == 0
    assert len(tr.diff.removed) == 0
    assert len(tr.diff.changed) == 0
    assert tr.any_truncated


def test_original_result_not_mutated():
    result = make_result(n_added=5)
    truncate_diff(result, TruncateOptions(max_added=2))
    assert len(result.added) == 5
