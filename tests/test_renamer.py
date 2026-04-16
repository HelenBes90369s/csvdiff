"""Tests for csvdiff.renamer."""
import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.renamer import RenameError, RenameOptions, rename_diff


def _fc(field, old, new):
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key, kind="changed", old=None, new=None, fcs=None):
    return RowChange(key=key, kind=kind, old_row=old or {}, new_row=new or {}, field_changes=fcs or [])


def make_result(added=None, removed=None, changed=None):
    return DiffResult(added=added or [], removed=removed or [], changed=changed or [])


def test_options_empty_mapping_raises():
    with pytest.raises(RenameError):
        RenameOptions(mapping={})


def test_options_blank_key_raises():
    with pytest.raises(RenameError):
        RenameOptions(mapping={" ": "b"})


def test_options_blank_value_raises():
    with pytest.raises(RenameError):
        RenameOptions(mapping={"a": ""})


def test_rename_diff_none_raises():
    opts = RenameOptions(mapping={"a": "b"})
    with pytest.raises(RenameError):
        rename_diff(None, opts)


def test_rename_added_rows():
    result = make_result(added=[{"name": "Alice", "age": "30"}])
    opts = RenameOptions(mapping={"name": "full_name"})
    out = rename_diff(result, opts)
    assert out.added == [{"full_name": "Alice", "age": "30"}]


def test_rename_removed_rows():
    result = make_result(removed=[{"name": "Bob", "score": "5"}])
    opts = RenameOptions(mapping={"score": "points"})
    out = rename_diff(result, opts)
    assert out.removed == [{"name": "Bob", "points": "5"}]


def test_rename_changed_row_fields():
    fc = _fc("name", "Alice", "Alicia")
    rc = _change(
        key=("1",),
        old={"name": "Alice"},
        new={"name": "Alicia"},
        fcs=[fc],
    )
    result = make_result(changed=[rc])
    opts = RenameOptions(mapping={"name": "full_name"})
    out = rename_diff(result, opts)
    rc_out = out.changed[0]
    assert rc_out.old_row == {"full_name": "Alice"}
    assert rc_out.new_row == {"full_name": "Alicia"}
    assert rc_out.field_changes[0].field == "full_name"


def test_rename_unmapped_columns_preserved():
    result = make_result(added=[{"id": "1", "val": "x"}])
    opts = RenameOptions(mapping={"val": "value"})
    out = rename_diff(result, opts)
    assert "id" in out.added[0]
    assert "value" in out.added[0]


def test_rename_empty_result():
    result = make_result()
    opts = RenameOptions(mapping={"a": "b"})
    out = rename_diff(result, opts)
    assert out.added == []
    assert out.removed == []
    assert out.changed == []
