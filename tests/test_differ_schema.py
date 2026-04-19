"""Tests for csvdiff.differ_schema."""
import pytest
from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.differ_schema import (
    SchemaError, ColumnSchema, DiffSchema, infer_schema, assert_schema_subset,
)


def _fc(field, old="a", new="b"):
    return FieldChange(field=field, old_value=old, new_value=new)


def _added(row):
    return RowChange(key=tuple(row.values())[:1], row=row, before={}, after=row, field_changes=[])


def _removed(row):
    return RowChange(key=tuple(row.values())[:1], row=row, before=row, after={}, field_changes=[])


def _changed(before, after, fcs):
    return RowChange(key=(before.get("id", "x"),), row=before, before=before, after=after, field_changes=fcs)


def make_result(added=None, removed=None, changed=None):
    return DiffResult(added=added or [], removed=removed or [], changed=changed or [])


def test_infer_schema_none_raises():
    with pytest.raises(SchemaError):
        infer_schema(None)


def test_infer_schema_empty_result():
    schema = infer_schema(make_result())
    assert schema.all_columns() == []
    assert schema.changed_columns() == []


def test_infer_schema_added_rows():
    r = make_result(added=[_added({"id": "1", "name": "Alice"})])
    schema = infer_schema(r)
    assert "id" in schema.columns
    assert schema.columns["id"].seen_in_added
    assert not schema.columns["id"].seen_in_changed


def test_infer_schema_removed_rows():
    r = make_result(removed=[_removed({"id": "2", "val": "x"})])
    schema = infer_schema(r)
    assert schema.columns["val"].seen_in_removed
    assert not schema.columns["val"].seen_in_added


def test_infer_schema_changed_rows():
    fc = _fc("score", "1", "2")
    r = make_result(changed=[_changed({"id": "3", "score": "1"}, {"id": "3", "score": "2"}, [fc])])
    schema = infer_schema(r)
    assert schema.columns["score"].seen_in_changed
    assert "score" in schema.changed_columns()


def test_column_schema_appears_in():
    cs = ColumnSchema(name="x", seen_in_added=True, seen_in_changed=True)
    kinds = cs.appears_in()
    assert "added" in kinds
    assert "changed" in kinds
    assert "removed" not in kinds


def test_assert_schema_subset_passes():
    r = make_result(added=[_added({"id": "1", "name": "A"})])
    schema = infer_schema(r)
    assert_schema_subset(schema, ["id", "name", "extra"])


def test_assert_schema_subset_raises_on_unknown():
    r = make_result(added=[_added({"id": "1", "secret": "x"})])
    schema = infer_schema(r)
    with pytest.raises(SchemaError, match="secret"):
        assert_schema_subset(schema, ["id"])


def test_diff_schema_all_columns_sorted():
    r = make_result(
        added=[_added({"z": "1", "a": "2"})],
        removed=[_removed({"m": "3"})],
    )
    schema = infer_schema(r)
    cols = schema.all_columns()
    assert cols == sorted(cols)
