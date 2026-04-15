"""Tests for csvdiff.aggregator."""
import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.aggregator import FieldAggregate, AggregateError, aggregate_diff


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key, *fcs) -> RowChange:
    return RowChange(key=key, field_changes=list(fcs))


def make_result(changed=(), added=(), removed=()) -> DiffResult:
    return DiffResult(
        added=list(added),
        removed=list(removed),
        changed=list(changed),
    )


def test_aggregate_empty_result_returns_empty_dict():
    result = make_result()
    assert aggregate_diff(result) == {}


def test_aggregate_none_raises():
    with pytest.raises(AggregateError):
        aggregate_diff(None)


def test_aggregate_single_numeric_field():
    change = _change(("1",), _fc("price", "10.0", "15.0"))
    result = make_result(changed=[change])
    aggs = aggregate_diff(result)
    assert "price" in aggs
    agg = aggs["price"]
    assert agg.count == 1
    assert agg.numeric_count == 1
    assert agg.total_delta == pytest.approx(5.0)
    assert agg.min_delta == pytest.approx(5.0)
    assert agg.max_delta == pytest.approx(5.0)
    assert agg.mean_delta == pytest.approx(5.0)


def test_aggregate_non_numeric_field_counts_but_no_delta():
    change = _change(("1",), _fc("name", "Alice", "Bob"))
    result = make_result(changed=[change])
    aggs = aggregate_diff(result)
    agg = aggs["name"]
    assert agg.count == 1
    assert agg.numeric_count == 0
    assert agg.mean_delta is None


def test_aggregate_multiple_rows_same_field():
    changes = [
        _change(("1",), _fc("qty", "2", "4")),
        _change(("2",), _fc("qty", "10", "8")),
    ]
    result = make_result(changed=changes)
    aggs = aggregate_diff(result)
    agg = aggs["qty"]
    assert agg.count == 2
    assert agg.numeric_count == 2
    assert agg.total_delta == pytest.approx(0.0)  # +2 and -2
    assert agg.min_delta == pytest.approx(-2.0)
    assert agg.max_delta == pytest.approx(2.0)


def test_aggregate_columns_filter_includes_only_named():
    change = _change(("1",), _fc("price", "1", "2"), _fc("qty", "5", "6"))
    result = make_result(changed=[change])
    aggs = aggregate_diff(result, columns=["price"])
    assert "price" in aggs
    assert "qty" not in aggs


def test_aggregate_columns_empty_name_raises():
    result = make_result()
    with pytest.raises(AggregateError):
        aggregate_diff(result, columns=[""])


def test_aggregate_columns_whitespace_name_raises():
    result = make_result()
    with pytest.raises(AggregateError):
        aggregate_diff(result, columns=["  "])


def test_aggregate_ignores_added_and_removed_rows():
    result = make_result(
        added=[{"id": "1", "price": "9.99"}],
        removed=[{"id": "2", "price": "4.99"}],
    )
    aggs = aggregate_diff(result)
    assert aggs == {}


def test_aggregate_mixed_numeric_and_non_numeric_old_value():
    change = _change(("1",), _fc("val", "N/A", "5.0"))
    result = make_result(changed=[change])
    aggs = aggregate_diff(result)
    agg = aggs["val"]
    assert agg.count == 1
    assert agg.numeric_count == 0
