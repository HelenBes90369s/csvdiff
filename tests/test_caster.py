"""Tests for csvdiff.caster."""
import pytest
from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.caster import CastError, CastOptions, cast_diff, _cast_value


def _fc(field, old, new):
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key, before, after, fcs):
    return RowChange(key=key, before=before, after=after, field_changes=fcs)


def make_result(changes=None):
    return DiffResult(added=[], removed=[], changes=changes or [])


def test_options_empty_columns_raises():
    with pytest.raises(CastError):
        CastOptions(columns={})


def test_options_invalid_type_raises():
    with pytest.raises(CastError):
        CastOptions(columns={"age": "str"})


def test_options_valid():
    opts = CastOptions(columns={"age": "int", "score": "float"})
    assert opts.columns["age"] == "int"


def test_cast_value_int():
    assert _cast_value("42", "int", True) == 42


def test_cast_value_float():
    assert _cast_value("3.14", "float", True) == pytest.approx(3.14)


def test_cast_value_bool_true():
    assert _cast_value("true", "bool", True) is True
    assert _cast_value("yes", "bool", True) is True
    assert _cast_value("1", "bool", True) is True


def test_cast_value_bool_false():
    assert _cast_value("false", "bool", True) is False


def test_cast_value_invalid_strict_raises():
    with pytest.raises(CastError):
        _cast_value("abc", "int", strict=True)


def test_cast_value_invalid_lenient_returns_original():
    assert _cast_value("abc", "int", strict=False) == "abc"


def test_cast_diff_none_raises():
    opts = CastOptions(columns={"age": "int"})
    with pytest.raises(CastError):
        cast_diff(None, opts)


def test_cast_diff_empty_result():
    opts = CastOptions(columns={"age": "int"})
    result = cast_diff(make_result(), opts)
    assert result.changes == []


def test_cast_diff_field_changes_converted():
    opts = CastOptions(columns={"age": "int"})
    change = _change(
        key=("1",),
        before={"id": "1", "age": "30"},
        after={"id": "1", "age": "31"},
        fcs=[_fc("age", "30", "31")],
    )
    result = cast_diff(make_result([change]), opts)
    fc = result.changes[0].field_changes[0]
    assert fc.old_value == 30
    assert fc.new_value == 31


def test_cast_diff_row_values_converted():
    opts = CastOptions(columns={"score": "float"})
    change = _change(
        key=("a",),
        before={"id": "a", "score": "1.5"},
        after={"id": "a", "score": "2.5"},
        fcs=[],
    )
    result = cast_diff(make_result([change]), opts)
    assert result.changes[0].before["score"] == pytest.approx(1.5)
    assert result.changes[0].after["score"] == pytest.approx(2.5)


def test_cast_diff_unrelated_columns_unchanged():
    opts = CastOptions(columns={"age": "int"})
    change = _change(
        key=("1",),
        before={"id": "1", "name": "Alice", "age": "25"},
        after={"id": "1", "name": "Alice", "age": "26"},
        fcs=[_fc("age", "25", "26")],
    )
    result = cast_diff(make_result([change]), opts)
    assert result.changes[0].before["name"] == "Alice"
