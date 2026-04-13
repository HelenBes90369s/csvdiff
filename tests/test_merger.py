"""Tests for csvdiff.merger."""

from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.merger import MergeError, merge_diff


def make_result(
    added=None,
    removed=None,
    changed=None,
) -> DiffResult:
    return DiffResult(
        added=added or {},
        removed=removed or {},
        changed=changed or {},
    )


BASE = [
    {"id": "1", "name": "Alice", "score": "10"},
    {"id": "2", "name": "Bob",   "score": "20"},
    {"id": "3", "name": "Carol", "score": "30"},
]


def test_merge_no_changes():
    diff = make_result()
    result = merge_diff(BASE, ["id"], diff)
    assert result == BASE


def test_merge_added_row():
    new_row = {"id": "4", "name": "Dave", "score": "40"}
    diff = make_result(added={("4",): new_row})
    result = merge_diff(BASE, ["id"], diff)
    assert result[-1] == new_row
    assert len(result) == 4


def test_merge_removed_row():
    diff = make_result(removed={("2",): BASE[1]})
    result = merge_diff(BASE, ["id"], diff)
    ids = [r["id"] for r in result]
    assert "2" not in ids
    assert len(result) == 2


def test_merge_changed_row():
    change = RowChange(
        key=("1",),
        old_row=BASE[0],
        new_row={"id": "1", "name": "Alice", "score": "99"},
        field_changes=[FieldChange(column="score", old_value="10", new_value="99")],
    )
    diff = make_result(changed={("1",): change})
    result = merge_diff(BASE, ["id"], diff)
    alice = next(r for r in result if r["id"] == "1")
    assert alice["score"] == "99"


def test_merge_remove_nonexistent_raises():
    diff = make_result(removed={("99",): {"id": "99", "name": "Ghost", "score": "0"}})
    with pytest.raises(MergeError, match="99"):
        merge_diff(BASE, ["id"], diff)


def test_merge_add_duplicate_raises():
    diff = make_result(added={("1",): BASE[0]})
    with pytest.raises(MergeError, match="already exists"):
        merge_diff(BASE, ["id"], diff)


def test_merge_no_key_columns_raises():
    with pytest.raises(MergeError, match="key column"):
        merge_diff(BASE, [], make_result())


def test_merge_preserves_order():
    diff = make_result(removed={("2",): BASE[1]})
    result = merge_diff(BASE, ["id"], diff)
    assert [r["id"] for r in result] == ["1", "3"]
