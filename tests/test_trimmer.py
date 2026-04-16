"""Tests for csvdiff.trimmer."""
import pytest
from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.trimmer import TrimError, TrimOptions, trim_diff


def _fc(field, old, new):
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key, old_row, new_row, fcs):
    return RowChange(key=key, old_row=old_row, new_row=new_row, field_changes=fcs)


def make_result(added=None, removed=None, changed=None):
    return DiffResult(added=added or [], removed=removed or [], changed=changed or [])


def test_trim_options_empty_columns_raises():
    with pytest.raises(TrimError):
        TrimOptions(columns=[])


def test_trim_options_none_columns_ok():
    opts = TrimOptions(columns=None)
    assert opts.columns is None


def test_trim_none_result_raises():
    with pytest.raises(TrimError):
        trim_diff(None)


def test_trim_empty_result_returns_empty():
    result = make_result()
    out = trim_diff(result)
    assert out.added == [] and out.removed == [] and out.changed == []


def test_trim_added_row_strips_values():
    result = make_result(added=[{"id": "1", "name": "  Alice  "}])
    out = trim_diff(result)
    assert out.added[0]["name"] == "Alice"


def test_trim_removed_row_strips_values():
    result = make_result(removed=[{"id": " 2 ", "val": " x "}])
    out = trim_diff(result)
    assert out.removed[0]["val"] == "x"


def test_trim_changed_row_field_changes():
    fc = _fc("name", "  Bob  ", "  Carol  ")
    rc = _change(("1",), {"id": "1", "name": "  Bob  "}, {"id": "1", "name": "  Carol  "}, [fc])
    result = make_result(changed=[rc])
    out = trim_diff(result)
    assert out.changed[0].field_changes[0].old_value == "Bob"
    assert out.changed[0].field_changes[0].new_value == "Carol"


def test_trim_specific_column_only():
    result = make_result(added=[{"id": "  1  ", "name": "  Alice  "}])
    opts = TrimOptions(columns=["name"])
    out = trim_diff(result, opts)
    assert out.added[0]["name"] == "Alice"
    assert out.added[0]["id"] == "  1  "  # untouched


def test_trim_keys_strips_column_names():
    result = make_result(added=[{" id ": "1", " name ": "Alice"}])
    opts = TrimOptions(trim_keys=True)
    out = trim_diff(result, opts)
    assert "id" in out.added[0]
    assert "name" in out.added[0]


def test_trim_non_string_values_unchanged():
    result = make_result(added=[{"id": "1", "count": 42}])
    out = trim_diff(result)
    assert out.added[0]["count"] == 42


def test_trim_field_change_respects_column_filter():
    fc = _fc("score", " 10 ", " 20 ")
    rc = _change(("1",), {}, {}, [fc])
    result = make_result(changed=[rc])
    opts = TrimOptions(columns=["name"])  # score not included
    out = trim_diff(result, opts)
    assert out.changed[0].field_changes[0].old_value == " 10 "
