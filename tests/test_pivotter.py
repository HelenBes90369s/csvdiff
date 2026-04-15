"""Tests for csvdiff.pivotter."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.pivotter import FieldPivot, PivotError, pivot_diff, sorted_pivots


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fc(name: str, old: str, new: str) -> FieldChange:
    return FieldChange(field_name=name, old_value=old, new_value=new)


def _change(key, *field_changes: FieldChange) -> RowChange:
    return RowChange(key=key, field_changes=list(field_changes))


def make_result(
    changed=None, added=None, removed=None
) -> DiffResult:
    return DiffResult(
        changed=changed or [],
        added=added or [],
        removed=removed or [],
    )


# ---------------------------------------------------------------------------
# pivot_diff
# ---------------------------------------------------------------------------

def test_pivot_diff_none_raises():
    with pytest.raises(PivotError):
        pivot_diff(None)  # type: ignore[arg-type]


def test_pivot_diff_empty_result_returns_empty_dict():
    result = make_result()
    assert pivot_diff(result) == {}


def test_pivot_diff_added_and_removed_rows_ignored():
    result = make_result(
        added=[("k1", {"a": "1"})],
        removed=[("k2", {"a": "2"})],
    )
    assert pivot_diff(result) == {}


def test_pivot_diff_single_changed_row():
    result = make_result(
        changed=[_change("row1", _fc("price", "10", "20"))]
    )
    pivots = pivot_diff(result)
    assert "price" in pivots
    assert pivots["price"].count == 1
    assert pivots["price"].old_values == ["10"]
    assert pivots["price"].new_values == ["20"]


def test_pivot_diff_multiple_fields_same_row():
    result = make_result(
        changed=[
            _change("row1", _fc("price", "10", "20"), _fc("qty", "1", "5"))
        ]
    )
    pivots = pivot_diff(result)
    assert set(pivots.keys()) == {"price", "qty"}
    assert pivots["price"].count == 1
    assert pivots["qty"].count == 1


def test_pivot_diff_same_field_multiple_rows():
    result = make_result(
        changed=[
            _change("row1", _fc("status", "A", "B")),
            _change("row2", _fc("status", "C", "D")),
        ]
    )
    pivots = pivot_diff(result)
    assert pivots["status"].count == 2
    assert pivots["status"].old_values == ["A", "C"]


def test_pivot_diff_tuple_key_repr():
    result = make_result(
        changed=[_change(("a", "b"), _fc("x", "1", "2"))]
    )
    pivots = pivot_diff(result)
    key_repr, _ = pivots["x"].changes[0]
    assert key_repr == "a|b"


# ---------------------------------------------------------------------------
# sorted_pivots
# ---------------------------------------------------------------------------

def test_sorted_pivots_descending_order():
    result = make_result(
        changed=[
            _change("r1", _fc("a", "1", "2")),
            _change("r2", _fc("a", "3", "4"), _fc("b", "5", "6")),
            _change("r3", _fc("a", "7", "8")),
        ]
    )
    order = sorted_pivots(result)
    assert order[0].field_name == "a"
    assert order[0].count == 3
    assert order[1].field_name == "b"
    assert order[1].count == 1


def test_sorted_pivots_ascending_order():
    result = make_result(
        changed=[
            _change("r1", _fc("a", "1", "2")),
            _change("r2", _fc("b", "3", "4"), _fc("b", "5", "6")),
        ]
    )
    order = sorted_pivots(result, descending=False)
    assert order[0].field_name == "a"
    assert order[-1].field_name == "b"
