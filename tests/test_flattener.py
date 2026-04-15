"""Tests for csvdiff.flattener."""

import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.flattener import FlatRow, FlattenError, flatten_diff


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key, row: dict, field_changes=None) -> RowChange:
    return RowChange(key=key, row=row, field_changes=field_changes or [])


def make_result(added=None, removed=None, changed=None) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


# ---------------------------------------------------------------------------
# FlatRow.as_dict
# ---------------------------------------------------------------------------

def test_flat_row_as_dict():
    fr = FlatRow(kind="added", key="k1", field="name", old_value=None, new_value="Alice")
    d = fr.as_dict()
    assert d == {"kind": "added", "key": "k1", "field": "name",
                 "old_value": None, "new_value": "Alice"}


# ---------------------------------------------------------------------------
# flatten_diff – basic cases
# ---------------------------------------------------------------------------

def test_flatten_empty_result_returns_empty_list():
    assert flatten_diff(make_result()) == []


def test_flatten_none_raises():
    with pytest.raises(FlattenError):
        flatten_diff(None)  # type: ignore[arg-type]


def test_flatten_added_row_produces_one_record_per_field():
    row = {"id": "1", "name": "Alice", "age": "30"}
    result = make_result(added=[_change("1", row)])
    flat = flatten_diff(result)
    assert len(flat) == 3
    kinds = {fr.kind for fr in flat}
    assert kinds == {"added"}
    fields = {fr.field for fr in flat}
    assert fields == {"id", "name", "age"}
    for fr in flat:
        assert fr.old_value is None
        assert fr.new_value is not None


def test_flatten_removed_row_produces_one_record_per_field():
    row = {"id": "2", "city": "London"}
    result = make_result(removed=[_change("2", row)])
    flat = flatten_diff(result)
    assert len(flat) == 2
    for fr in flat:
        assert fr.kind == "removed"
        assert fr.new_value is None


def test_flatten_changed_row_produces_one_record_per_field_change():
    fcs = [_fc("name", "Bob", "Robert"), _fc("age", "25", "26")]
    change = _change("3", {"id": "3", "name": "Robert", "age": "26"}, fcs)
    result = make_result(changed=[change])
    flat = flatten_diff(result)
    assert len(flat) == 2
    for fr in flat:
        assert fr.kind == "changed"
        assert fr.key == "3"
        assert fr.old_value is not None
        assert fr.new_value is not None


def test_flatten_tuple_key_joined_with_pipe():
    row = {"a": "x", "b": "y"}
    result = make_result(added=[_change(("x", "y"), row)])
    flat = flatten_diff(result)
    assert all(fr.key == "x|y" for fr in flat)


def test_flatten_mixed_result_order_added_removed_changed():
    added = [_change("1", {"id": "1"})]
    removed = [_change("2", {"id": "2"})]
    changed = [_change("3", {"id": "3"}, [_fc("val", "a", "b")])]
    result = make_result(added=added, removed=removed, changed=changed)
    flat = flatten_diff(result)
    kinds = [fr.kind for fr in flat]
    # added first, then removed, then changed
    assert kinds[0] == "added"
    assert "removed" in kinds
    assert "changed" in kinds
