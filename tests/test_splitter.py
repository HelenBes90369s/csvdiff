"""Tests for csvdiff.splitter."""

from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.splitter import SplitError, SplitOptions, bucket_keys, split_diff


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(
    key,
    old_row=None,
    new_row=None,
    field_changes=None,
) -> RowChange:
    return RowChange(
        key=key,
        old_row=old_row,
        new_row=new_row,
        field_changes=field_changes or [],
    )


def make_result(changes=None) -> DiffResult:
    return DiffResult(changes=changes or [], added_rows=[], removed_rows=[])


# ---------------------------------------------------------------------------
# SplitOptions validation
# ---------------------------------------------------------------------------

def test_split_options_empty_column_raises():
    with pytest.raises(SplitError):
        SplitOptions(column="")


def test_split_options_whitespace_column_raises():
    with pytest.raises(SplitError):
        SplitOptions(column="   ")


def test_split_options_valid():
    opts = SplitOptions(column="region")
    assert opts.column == "region"
    assert opts.include_unchanged is False


# ---------------------------------------------------------------------------
# split_diff
# ---------------------------------------------------------------------------

def test_split_diff_none_result_raises():
    with pytest.raises(SplitError):
        split_diff(None, SplitOptions(column="region"))


def test_split_diff_empty_result_returns_empty_dict():
    result = make_result()
    out = split_diff(result, SplitOptions(column="region"))
    assert out == {}


def test_split_diff_single_bucket():
    c = _change(("1",), new_row={"id": "1", "region": "EU"}, field_changes=[_fc("v", "a", "b")])
    result = make_result([c])
    out = split_diff(result, SplitOptions(column="region"))
    assert list(out.keys()) == ["EU"]
    assert len(out["EU"].changes) == 1


def test_split_diff_multiple_buckets():
    c1 = _change(("1",), new_row={"id": "1", "region": "EU"}, field_changes=[_fc("v", "a", "b")])
    c2 = _change(("2",), new_row={"id": "2", "region": "US"}, field_changes=[_fc("v", "x", "y")])
    c3 = _change(("3",), new_row={"id": "3", "region": "EU"}, field_changes=[_fc("v", "p", "q")])
    result = make_result([c1, c2, c3])
    out = split_diff(result, SplitOptions(column="region"))
    assert set(out.keys()) == {"EU", "US"}
    assert len(out["EU"].changes) == 2
    assert len(out["US"].changes) == 1


def test_split_diff_missing_column_uses_missing_key():
    c = _change(("1",), new_row={"id": "1"}, field_changes=[_fc("v", "a", "b")])
    result = make_result([c])
    out = split_diff(result, SplitOptions(column="region"))
    assert "__missing__" in out


def test_split_diff_prefers_new_row_for_key():
    c = _change(
        ("1",),
        old_row={"id": "1", "region": "EU"},
        new_row={"id": "1", "region": "US"},
        field_changes=[_fc("region", "EU", "US")],
    )
    result = make_result([c])
    out = split_diff(result, SplitOptions(column="region"))
    assert "US" in out
    assert "EU" not in out


# ---------------------------------------------------------------------------
# bucket_keys
# ---------------------------------------------------------------------------

def test_bucket_keys_empty_result():
    assert bucket_keys(make_result(), SplitOptions(column="region")) == []


def test_bucket_keys_returns_sorted():
    changes = [
        _change((str(i),), new_row={"id": str(i), "region": r}, field_changes=[])
        for i, r in enumerate(["US", "EU", "APAC"])
    ]
    result = make_result(changes)
    assert bucket_keys(result, SplitOptions(column="region")) == ["APAC", "EU", "US"]


def test_bucket_keys_none_result_raises():
    with pytest.raises(SplitError):
        bucket_keys(None, SplitOptions(column="region"))
