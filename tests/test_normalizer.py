"""Tests for csvdiff.normalizer."""

import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.normalizer import (
    NormalizeError,
    NormalizeOptions,
    normalize_value,
    normalize_row,
    normalize_rows,
    normalize_diff,
)


# ---------------------------------------------------------------------------
# NormalizeOptions validation
# ---------------------------------------------------------------------------

def test_normalize_options_empty_columns_raises():
    with pytest.raises(NormalizeError):
        NormalizeOptions(columns=[])


def test_normalize_options_defaults_are_safe():
    opts = NormalizeOptions()
    assert opts.strip_whitespace is True
    assert opts.lowercase is False
    assert opts.columns is None


# ---------------------------------------------------------------------------
# normalize_value
# ---------------------------------------------------------------------------

def test_normalize_value_strips_whitespace():
    opts = NormalizeOptions(strip_whitespace=True, lowercase=False)
    assert normalize_value("  hello  ", opts) == "hello"


def test_normalize_value_lowercase():
    opts = NormalizeOptions(strip_whitespace=False, lowercase=True)
    assert normalize_value("Hello World", opts) == "hello world"


def test_normalize_value_both():
    opts = NormalizeOptions(strip_whitespace=True, lowercase=True)
    assert normalize_value("  FOO  ", opts) == "foo"


def test_normalize_value_neither():
    opts = NormalizeOptions(strip_whitespace=False, lowercase=False)
    assert normalize_value("  FOO  ", opts) == "  FOO  "


# ---------------------------------------------------------------------------
# normalize_row
# ---------------------------------------------------------------------------

def test_normalize_row_all_columns():
    opts = NormalizeOptions(strip_whitespace=True, lowercase=True)
    row = {"name": "  Alice  ", "city": "LONDON"}
    result = normalize_row(row, opts)
    assert result == {"name": "alice", "city": "london"}


def test_normalize_row_selected_columns_only():
    opts = NormalizeOptions(strip_whitespace=True, lowercase=True, columns=["name"])
    row = {"name": "  Alice  ", "city": "LONDON"}
    result = normalize_row(row, opts)
    assert result["name"] == "alice"
    assert result["city"] == "LONDON"  # untouched


# ---------------------------------------------------------------------------
# normalize_rows
# ---------------------------------------------------------------------------

def test_normalize_rows_returns_list():
    opts = NormalizeOptions()
    rows = [{"a": "  x  "}, {"a": "  y  "}]
    result = normalize_rows(rows, opts)
    assert result == [{"a": "x"}, {"a": "y"}]


# ---------------------------------------------------------------------------
# normalize_diff
# ---------------------------------------------------------------------------

def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(kind: str, key: tuple, old: dict, new: dict, fcs=None) -> RowChange:
    return RowChange(key=key, kind=kind, old_row=old, new_row=new,
                     field_changes=fcs or [])


def test_normalize_diff_strips_values_in_changed():
    opts = NormalizeOptions(strip_whitespace=True)
    rc = _change(
        "changed", ("1",),
        {"id": "1", "name": "  old  "},
        {"id": "1", "name": "  new  "},
        [_fc("name", "  old  ", "  new  ")],
    )
    result = normalize_diff(DiffResult(added=[], removed=[], changed=[rc]), opts)
    ch = result.changed[0]
    assert ch.old_row["name"] == "old"
    assert ch.new_row["name"] == "new"
    assert ch.field_changes[0].old_value == "old"
    assert ch.field_changes[0].new_value == "new"


def test_normalize_diff_added_and_removed():
    opts = NormalizeOptions(lowercase=True)
    added = _change("added", ("2",), {}, {"id": "2", "val": "HELLO"}, [])
    removed = _change("removed", ("3",), {"id": "3", "val": "WORLD"}, {}, [])
    result = normalize_diff(
        DiffResult(added=[added], removed=[removed], changed=[]), opts
    )
    assert result.added[0].new_row["val"] == "hello"
    assert result.removed[0].old_row["val"] == "world"
