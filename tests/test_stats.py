"""Tests for csvdiff.stats."""

from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.stats import DiffStats, compute_stats, format_stats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_field_change(field: str, old: str, new: str):
    from csvdiff.differ import changed_fields  # noqa: F401 – just verify import
    # Build a minimal object that looks like a FieldChange.
    class FC:
        pass
    fc = FC()
    fc.field = field
    fc.old_value = old
    fc.new_value = new
    return fc


def make_change(key, field_changes=None):
    rc = RowChange.__new__(RowChange)
    rc.key = key
    rc.field_changes = field_changes or []
    return rc


def make_result(added=None, removed=None, changed=None, total_rows=None):
    dr = DiffResult.__new__(DiffResult)
    dr.added = added or []
    dr.removed = removed or []
    dr.changed = changed or []
    if total_rows is not None:
        dr.total_rows = total_rows
    return dr


# ---------------------------------------------------------------------------
# compute_stats
# ---------------------------------------------------------------------------

def test_compute_stats_empty():
    result = make_result(total_rows=0)
    stats = compute_stats(result)
    assert stats.total_added == 0
    assert stats.total_removed == 0
    assert stats.total_changed == 0
    assert stats.total_unchanged == 0
    assert stats.change_ratio == 0.0
    assert stats.changed_fields == {}


def test_compute_stats_added_only():
    result = make_result(added=[{"id": "1"}], total_rows=1)
    stats = compute_stats(result)
    assert stats.total_added == 1
    assert stats.total_removed == 0
    assert stats.total_changed == 0
    assert stats.change_ratio == pytest.approx(1.0)


def test_compute_stats_changed_fields_counted():
    fc1 = _make_field_change("price", "10", "20")
    fc2 = _make_field_change("price", "5", "15")
    fc3 = _make_field_change("name", "Alice", "Bob")
    changes = [
        make_change(("1",), [fc1]),
        make_change(("2",), [fc2, fc3]),
    ]
    result = make_result(changed=changes, total_rows=5)
    stats = compute_stats(result)
    assert stats.changed_fields["price"] == 2
    assert stats.changed_fields["name"] == 1
    assert stats.total_changed == 2
    assert stats.total_unchanged == 3


def test_most_changed_fields_order():
    fc_a = _make_field_change("a", "1", "2")
    fc_b1 = _make_field_change("b", "x", "y")
    fc_b2 = _make_field_change("b", "p", "q")
    changes = [
        make_change(("1",), [fc_a, fc_b1]),
        make_change(("2",), [fc_b2]),
    ]
    result = make_result(changed=changes, total_rows=2)
    stats = compute_stats(result)
    assert stats.most_changed_fields[0] == "b"


def test_change_ratio_partial():
    result = make_result(added=[{"id": "1"}], total_rows=4)
    stats = compute_stats(result)
    assert stats.change_ratio == pytest.approx(0.25)


# ---------------------------------------------------------------------------
# format_stats
# ---------------------------------------------------------------------------

def test_format_stats_contains_key_labels():
    result = make_result(
        added=[{"id": "1"}],
        removed=[{"id": "2"}],
        total_rows=10,
    )
    stats = compute_stats(result)
    output = format_stats(stats)
    assert "Added" in output
    assert "Removed" in output
    assert "Change ratio" in output


def test_format_stats_no_top_fields_when_empty():
    result = make_result(total_rows=3)
    stats = compute_stats(result)
    output = format_stats(stats)
    assert "Top fields" not in output
