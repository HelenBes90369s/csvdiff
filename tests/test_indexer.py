"""Tests for csvdiff.indexer."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.indexer import DiffIndex, IndexError, build_index


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fc(f: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=f, old_value=old, new_value=new)


def _change(
    key,
    kind: str = "changed",
    field_changes=None,
    old_row=None,
    new_row=None,
) -> RowChange:
    return RowChange(
        key=key,
        kind=kind,
        old_row=old_row or {},
        new_row=new_row or {},
        field_changes=field_changes or [],
    )


def make_result(
    added=None, removed=None, changed=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_build_index_none_raises():
    with pytest.raises(IndexError, match="None"):
        build_index(None)


def test_build_index_empty_result():
    idx = build_index(make_result())
    assert idx.size == 0
    assert idx.by_key == {}
    assert idx.by_field == {}


def test_build_index_added_row_indexed_by_key():
    change = _change(("id", "1"), kind="added", new_row={"id": "1", "name": "Alice"})
    idx = build_index(make_result(added=[change]))
    assert idx.size == 1
    assert idx.get_by_key(("id", "1")) == [change]


def test_build_index_removed_row_indexed_by_key():
    change = _change(("id", "2"), kind="removed", old_row={"id": "2", "name": "Bob"})
    idx = build_index(make_result(removed=[change]))
    assert idx.get_by_key(("id", "2")) == [change]


def test_build_index_changed_row_indexed_by_field():
    fc = _fc("price", "10", "20")
    change = _change(("sku", "A1"), kind="changed", field_changes=[fc])
    idx = build_index(make_result(changed=[change]))
    assert idx.get_by_field("price") == [change]


def test_build_index_unknown_field_returns_empty():
    idx = build_index(make_result())
    assert idx.get_by_field("nonexistent") == []


def test_build_index_positional_order():
    a = _change(("id", "1"), kind="added")
    r = _change(("id", "2"), kind="removed")
    c = _change(("id", "3"), kind="changed")
    idx = build_index(make_result(added=[a], removed=[r], changed=[c]))
    assert idx.get_by_position(0) is a
    assert idx.get_by_position(1) is r
    assert idx.get_by_position(2) is c
    assert idx.get_by_position(99) is None


def test_build_index_multiple_changes_same_field():
    fc1 = _fc("score", "1", "2")
    fc2 = _fc("score", "3", "4")
    c1 = _change(("id", "1"), kind="changed", field_changes=[fc1])
    c2 = _change(("id", "2"), kind="changed", field_changes=[fc2])
    idx = build_index(make_result(changed=[c1, c2]))
    assert len(idx.get_by_field("score")) == 2


def test_diff_index_size_counts_all_kinds():
    added = [_change(("id", str(i)), kind="added") for i in range(3)]
    removed = [_change(("id", str(i + 10)), kind="removed") for i in range(2)]
    idx = build_index(make_result(added=added, removed=removed))
    assert idx.size == 5
