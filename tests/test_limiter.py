"""Tests for csvdiff.limiter."""

import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.limiter import (
    LimitError,
    LimitOptions,
    LimitResult,
    limit_diff,
)


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def make_change(key: tuple, kind: str = "changed") -> RowChange:
    if kind == "added":
        return RowChange(key=key, kind="added", old_row={}, new_row={"id": key[0]})
    if kind == "removed":
        return RowChange(key=key, kind="removed", old_row={"id": key[0]}, new_row={})
    return RowChange(
        key=key,
        kind="changed",
        old_row={"id": key[0], "v": "a"},
        new_row={"id": key[0], "v": "b"},
        field_changes=[_fc("v", "a", "b")],
    )


def make_result(
    added=None, removed=None, changed=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


# --- LimitOptions validation ---

def test_limit_options_negative_max_added_raises():
    with pytest.raises(LimitError):
        LimitOptions(max_added=-1)


def test_limit_options_negative_max_removed_raises():
    with pytest.raises(LimitError):
        LimitOptions(max_removed=-1)


def test_limit_options_negative_max_changed_raises():
    with pytest.raises(LimitError):
        LimitOptions(max_changed=-1)


def test_limit_options_zero_is_valid():
    opts = LimitOptions(max_added=0, max_removed=0, max_changed=0)
    assert opts.max_added == 0


# --- limit_diff behaviour ---

def test_limit_diff_no_limits_returns_all():
    result = make_result(
        added=[make_change(("1",), "added"), make_change(("2",), "added")],
        removed=[make_change(("3",), "removed")],
        changed=[make_change(("4",))],
    )
    lr = limit_diff(result, LimitOptions())
    assert len(lr.result.added) == 2
    assert len(lr.result.removed) == 1
    assert len(lr.result.changed) == 1
    assert not lr.any_truncated


def test_limit_diff_caps_added():
    result = make_result(
        added=[make_change((str(i),), "added") for i in range(5)]
    )
    lr = limit_diff(result, LimitOptions(max_added=2))
    assert len(lr.result.added) == 2
    assert lr.added_truncated is True
    assert lr.removed_truncated is False
    assert lr.changed_truncated is False


def test_limit_diff_caps_removed():
    result = make_result(
        removed=[make_change((str(i),), "removed") for i in range(4)]
    )
    lr = limit_diff(result, LimitOptions(max_removed=1))
    assert len(lr.result.removed) == 1
    assert lr.removed_truncated is True


def test_limit_diff_caps_changed():
    result = make_result(
        changed=[make_change((str(i),)) for i in range(6)]
    )
    lr = limit_diff(result, LimitOptions(max_changed=3))
    assert len(lr.result.changed) == 3
    assert lr.changed_truncated is True


def test_limit_diff_exact_limit_not_truncated():
    result = make_result(
        added=[make_change(("1",), "added"), make_change(("2",), "added")]
    )
    lr = limit_diff(result, LimitOptions(max_added=2))
    assert not lr.added_truncated


def test_limit_diff_zero_limit_empties_category():
    result = make_result(
        added=[make_change(("1",), "added")],
        changed=[make_change(("2",))],
    )
    lr = limit_diff(result, LimitOptions(max_added=0, max_changed=0))
    assert lr.result.added == []
    assert lr.result.changed == []
    assert lr.added_truncated is True
    assert lr.changed_truncated is True


def test_any_truncated_false_when_none_truncated():
    result = make_result()
    lr = limit_diff(result, LimitOptions(max_added=10))
    assert not lr.any_truncated


def test_any_truncated_true_when_one_truncated():
    result = make_result(
        removed=[make_change((str(i),), "removed") for i in range(3)]
    )
    lr = limit_diff(result, LimitOptions(max_removed=1))
    assert lr.any_truncated is True
