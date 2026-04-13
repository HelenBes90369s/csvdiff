"""Tests for csvdiff.summary module."""

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.summary import DiffSummary, summarize, format_summary


def make_result(added=None, removed=None, changed=None) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


def make_change(key=("k",), field="col", old="a", new="b") -> RowChange:
    return RowChange(key=key, field=field, old_value=old, new_value=new)


def test_summarize_no_changes():
    result = make_result()
    s = summarize(result, rows_left=5, rows_right=5)
    assert s.added == 0
    assert s.removed == 0
    assert s.changed == 0
    assert s.unchanged == 5
    assert not s.has_changes


def test_summarize_added_rows():
    result = make_result(added=[
        {"id": "3", "name": "Carol"},
        {"id": "4", "name": "Dave"},
    ])
    s = summarize(result, rows_left=3, rows_right=5)
    assert s.added == 2
    assert s.removed == 0
    assert s.changed == 0
    assert s.unchanged == 3
    assert s.has_changes


def test_summarize_removed_rows():
    result = make_result(removed=[{"id": "1", "name": "Alice"}])
    s = summarize(result, rows_left=3, rows_right=2)
    assert s.removed == 1
    assert s.unchanged == 2


def test_summarize_changed_rows():
    result = make_result(changed=[make_change()])
    s = summarize(result, rows_left=4, rows_right=4)
    assert s.changed == 1
    assert s.unchanged == 3


def test_change_rate_zero_left_rows():
    result = make_result(added=[{"id": "1"}])
    s = summarize(result, rows_left=0, rows_right=1)
    assert s.change_rate == 0.0


def test_change_rate_calculation():
    result = make_result(
        removed=[{"id": "1"}],
        changed=[make_change()],
    )
    s = summarize(result, rows_left=4, rows_right=4)
    # 1 removed + 1 changed out of 4 left = 0.5
    assert s.change_rate == pytest.approx(0.5)


def test_format_summary_contains_counts():
    result = make_result(
        added=[{"id": "5"}],
        removed=[{"id": "1"}],
        changed=[make_change()],
    )
    s = summarize(result, rows_left=5, rows_right=5)
    text = format_summary(s)
    assert "Added:" in text
    assert "Removed:" in text
    assert "Changed:" in text
    assert "Unchanged:" in text
    assert "Change rate:" in text
    assert "40.0%" in text  # (1 removed + 1 changed) / 5


def test_unchanged_never_negative():
    # More changed than rows_left (edge case guard)
    result = make_result(changed=[make_change(), make_change(), make_change()])
    s = summarize(result, rows_left=2, rows_right=2)
    assert s.unchanged >= 0
