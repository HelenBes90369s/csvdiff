"""Tests for csvdiff.comparer."""

import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.comparer import (
    CompareError,
    CompareResult,
    FieldOverlap,
    compare_results,
)


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key: dict, field_changes=None) -> RowChange:
    return RowChange(key=key, field_changes=field_changes or [])


def make_result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes))


# ---------------------------------------------------------------------------
# Basic structural tests
# ---------------------------------------------------------------------------

def test_compare_both_empty():
    result = compare_results(make_result(), make_result())
    assert result.common_keys == 0
    assert result.only_in_left == 0
    assert result.only_in_right == 0
    assert result.field_overlaps == []
    assert result.overall_agreement == 1.0


def test_compare_none_raises():
    with pytest.raises(CompareError):
        compare_results(None, make_result())  # type: ignore


def test_compare_none_right_raises():
    with pytest.raises(CompareError):
        compare_results(make_result(), None)  # type: ignore


# ---------------------------------------------------------------------------
# Key distribution
# ---------------------------------------------------------------------------

def test_only_in_left():
    left = make_result(_change({"id": "1"}))
    right = make_result()
    result = compare_results(left, right)
    assert result.only_in_left == 1
    assert result.only_in_right == 0
    assert result.common_keys == 0


def test_only_in_right():
    left = make_result()
    right = make_result(_change({"id": "2"}))
    result = compare_results(left, right)
    assert result.only_in_right == 1
    assert result.only_in_left == 0


def test_common_keys_counted():
    change = _change({"id": "1"}, [_fc("name", "Alice", "Bob")])
    result = compare_results(make_result(change), make_result(change))
    assert result.common_keys == 1


# ---------------------------------------------------------------------------
# Field overlap agreement
# ---------------------------------------------------------------------------

def test_identical_changes_full_agreement():
    change = _change({"id": "1"}, [_fc("name", "Alice", "Bob")])
    result = compare_results(make_result(change), make_result(change))
    assert len(result.field_overlaps) == 1
    fo = result.field_overlaps[0]
    assert fo.field == "name"
    assert fo.agree == 1
    assert fo.disagree == 0
    assert fo.agreement_rate == 1.0


def test_differing_changes_disagree():
    left_change = _change({"id": "1"}, [_fc("name", "Alice", "Bob")])
    right_change = _change({"id": "1"}, [_fc("name", "Alice", "Charlie")])
    result = compare_results(make_result(left_change), make_result(right_change))
    fo = result.field_overlaps[0]
    assert fo.disagree == 1
    assert fo.agree == 0
    assert fo.agreement_rate == 0.0


def test_overall_agreement_mixed():
    c1 = _change({"id": "1"}, [_fc("a", "x", "y"), _fc("b", "1", "2")])
    c2 = _change({"id": "1"}, [_fc("a", "x", "y"), _fc("b", "1", "9")])
    result = compare_results(make_result(c1), make_result(c2))
    # field 'a' agrees, field 'b' disagrees -> 0.5
    assert result.overall_agreement == pytest.approx(0.5)


def test_field_overlap_agreement_rate_zero_total():
    fo = FieldOverlap(field="x", agree=0, disagree=0)
    assert fo.agreement_rate == 1.0


def test_multiple_common_keys_aggregate():
    c1a = _change({"id": "1"}, [_fc("v", "a", "b")])
    c2a = _change({"id": "2"}, [_fc("v", "a", "b")])
    c1b = _change({"id": "1"}, [_fc("v", "a", "b")])
    c2b = _change({"id": "2"}, [_fc("v", "a", "Z")])
    result = compare_results(make_result(c1a, c2a), make_result(c1b, c2b))
    fo = result.field_overlaps[0]
    assert fo.field == "v"
    assert fo.agree == 1
    assert fo.disagree == 1
    assert fo.agreement_rate == pytest.approx(0.5)
