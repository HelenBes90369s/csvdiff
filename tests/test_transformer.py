"""Tests for csvdiff.transformer."""

from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.transformer import (
    TransformError,
    TransformOptions,
    transform_diff,
)


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(
    key: tuple,
    old: dict,
    new: dict,
    field_changes: list,
) -> RowChange:
    return RowChange(key=key, old_row=old, new_row=new, field_changes=field_changes)


def make_result(
    added=None, removed=None, changed=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


# ---------------------------------------------------------------------------
# TransformOptions validation
# ---------------------------------------------------------------------------

def test_options_invalid_column_transforms_raises():
    with pytest.raises(TransformError):
        TransformOptions(column_transforms="bad")  # type: ignore


def test_options_defaults_are_safe():
    opts = TransformOptions()
    assert opts.column_transforms == {}
    assert opts.apply_to_old is True
    assert opts.apply_to_new is True


# ---------------------------------------------------------------------------
# transform_diff – basic behaviour
# ---------------------------------------------------------------------------

def test_transform_diff_none_result_raises():
    with pytest.raises(TransformError):
        transform_diff(None)


def test_transform_diff_empty_result_returns_empty():
    result = make_result()
    out = transform_diff(result)
    assert out.changed == []
    assert out.added == []
    assert out.removed == []


def test_transform_diff_uppercase_field():
    change = _change(
        key=("1",),
        old={"id": "1", "name": "alice"},
        new={"id": "1", "name": "ALICE"},
        field_changes=[_fc("name", "alice", "ALICE")],
    )
    result = make_result(changed=[change])
    opts = TransformOptions(column_transforms={"name": str.upper})
    out = transform_diff(result, opts)
    assert len(out.changed) == 1
    fc = out.changed[0].field_changes[0]
    assert fc.old_value == "ALICE"
    assert fc.new_value == "ALICE"


def test_transform_diff_only_applies_to_new_when_flagged():
    change = _change(
        key=("1",),
        old={"id": "1", "val": "hello"},
        new={"id": "1", "val": "world"},
        field_changes=[_fc("val", "hello", "world")],
    )
    result = make_result(changed=[change])
    opts = TransformOptions(
        column_transforms={"val": str.upper},
        apply_to_old=False,
        apply_to_new=True,
    )
    out = transform_diff(result, opts)
    fc = out.changed[0].field_changes[0]
    assert fc.old_value == "hello"  # untouched
    assert fc.new_value == "WORLD"


def test_transform_diff_skips_missing_column():
    change = _change(
        key=("1",),
        old={"id": "1", "score": "10"},
        new={"id": "1", "score": "20"},
        field_changes=[_fc("score", "10", "20")],
    )
    result = make_result(changed=[change])
    opts = TransformOptions(column_transforms={"nonexistent": str.upper})
    out = transform_diff(result, opts)
    fc = out.changed[0].field_changes[0]
    assert fc.old_value == "10"
    assert fc.new_value == "20"


def test_transform_diff_added_and_removed_are_preserved():
    added = [{"id": "2", "name": "bob"}]
    removed = [{"id": "3", "name": "carol"}]
    result = make_result(added=added, removed=removed)
    opts = TransformOptions(column_transforms={"name": str.upper})
    out = transform_diff(result, opts)
    assert out.added == added
    assert out.removed == removed


def test_transform_diff_no_opts_is_identity():
    change = _change(
        key=("1",),
        old={"id": "1", "x": "a"},
        new={"id": "1", "x": "b"},
        field_changes=[_fc("x", "a", "b")],
    )
    result = make_result(changed=[change])
    out = transform_diff(result)
    fc = out.changed[0].field_changes[0]
    assert fc.old_value == "a"
    assert fc.new_value == "b"
