"""Tests for csvdiff.filter module."""

import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.filter import (
    FilterError,
    exclude_columns,
    filter_columns,
    filter_diff_by_columns,
)


ROWS = [
    {"id": "1", "name": "Alice", "age": "30"},
    {"id": "2", "name": "Bob", "age": "25"},
]


def make_result() -> DiffResult:
    return DiffResult(
        added=[{"id": "3", "name": "Carol", "age": "28"}],
        removed=[{"id": "4", "name": "Dave", "age": "40"}],
        changed=[
            RowChange(
                key=("1",),
                old={"id": "1", "name": "Alice", "age": "30"},
                new={"id": "1", "name": "Alice", "age": "31"},
            )
        ],
    )


# --- filter_columns ---

def test_filter_columns_basic():
    result = filter_columns(ROWS, ["id", "name"])
    assert result == [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]


def test_filter_columns_single():
    result = filter_columns(ROWS, ["age"])
    assert result == [{"age": "30"}, {"age": "25"}]


def test_filter_columns_empty_rows():
    assert filter_columns([], ["id"]) == []


def test_filter_columns_missing_column_raises():
    with pytest.raises(FilterError, match="nonexistent"):
        filter_columns(ROWS, ["id", "nonexistent"])


# --- exclude_columns ---

def test_exclude_columns_basic():
    result = exclude_columns(ROWS, ["age"])
    assert result == [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]


def test_exclude_columns_empty_exclude():
    assert exclude_columns(ROWS, []) == ROWS


def test_exclude_columns_empty_rows():
    assert exclude_columns([], ["id"]) == []


# --- filter_diff_by_columns ---

def test_filter_diff_no_columns_returns_unchanged():
    result = make_result()
    assert filter_diff_by_columns(result, None) is result
    assert filter_diff_by_columns(result, []) is result


def test_filter_diff_added_rows():
    filtered = filter_diff_by_columns(make_result(), ["id", "name"])
    assert filtered["added"] == [{"id": "3", "name": "Carol"}]


def test_filter_diff_removed_rows():
    filtered = filter_diff_by_columns(make_result(), ["id", "name"])
    assert filtered["removed"] == [{"id": "4", "name": "Dave"}]


def test_filter_diff_changed_rows():
    filtered = filter_diff_by_columns(make_result(), ["id", "age"])
    changed = filtered["changed"]
    assert len(changed) == 1
    assert changed[0].old == {"id": "1", "age": "30"}
    assert changed[0].new == {"id": "1", "age": "31"}
    assert changed[0].key == ("1",)
