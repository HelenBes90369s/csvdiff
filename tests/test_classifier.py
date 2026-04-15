"""Tests for csvdiff.classifier."""

from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.classifier import (
    ClassifiedChange,
    ClassifyError,
    ClassifyOptions,
    classify_diff,
    severity_counts,
)


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(kind: str, key: tuple, changes=None) -> RowChange:
    row = {"id": key[0]}
    return RowChange(kind=kind, key=key, row=row, changes=changes or [])


def make_result(*changes: RowChange) -> DiffResult:
    return DiffResult(changes=list(changes))


# ---------------------------------------------------------------------------
# ClassifyOptions validation
# ---------------------------------------------------------------------------

def test_classify_options_overlap_raises():
    with pytest.raises(ClassifyError, match="critical and warning"):
        ClassifyOptions(
            critical_fields=frozenset({"price"}),
            warning_fields=frozenset({"price", "name"}),
        )


def test_classify_options_disjoint_ok():
    opts = ClassifyOptions(
        critical_fields=frozenset({"price"}),
        warning_fields=frozenset({"name"}),
    )
    assert "price" in opts.critical_fields


# ---------------------------------------------------------------------------
# classify_diff
# ---------------------------------------------------------------------------

def test_classify_empty_result():
    opts = ClassifyOptions(critical_fields=frozenset(), warning_fields=frozenset())
    assert classify_diff(make_result(), opts) == []


def test_classify_added_row_is_info():
    opts = ClassifyOptions(critical_fields=frozenset({"price"}), warning_fields=frozenset())
    result = make_result(_change("added", ("1",)))
    classified = classify_diff(result, opts)
    assert len(classified) == 1
    assert classified[0].severity == "info"


def test_classify_removed_row_is_info():
    opts = ClassifyOptions(critical_fields=frozenset({"price"}), warning_fields=frozenset())
    result = make_result(_change("removed", ("1",)))
    classified = classify_diff(result, opts)
    assert classified[0].severity == "info"


def test_classify_changed_critical_field():
    opts = ClassifyOptions(critical_fields=frozenset({"price"}), warning_fields=frozenset({"name"}))
    change = _change("changed", ("1",), changes=[_fc("price", "10", "20")])
    classified = classify_diff(make_result(change), opts)
    assert classified[0].severity == "critical"


def test_classify_changed_warning_field():
    opts = ClassifyOptions(critical_fields=frozenset({"price"}), warning_fields=frozenset({"name"}))
    change = _change("changed", ("1",), changes=[_fc("name", "Alice", "Bob")])
    classified = classify_diff(make_result(change), opts)
    assert classified[0].severity == "warning"


def test_classify_changed_info_field():
    opts = ClassifyOptions(critical_fields=frozenset({"price"}), warning_fields=frozenset({"name"}))
    change = _change("changed", ("1",), changes=[_fc("notes", "a", "b")])
    classified = classify_diff(make_result(change), opts)
    assert classified[0].severity == "info"


def test_classify_critical_takes_precedence_over_warning():
    opts = ClassifyOptions(
        critical_fields=frozenset({"price"}),
        warning_fields=frozenset({"name"}),
    )
    change = _change("changed", ("1",), changes=[_fc("price", "1", "2"), _fc("name", "A", "B")])
    classified = classify_diff(make_result(change), opts)
    assert classified[0].severity == "critical"


# ---------------------------------------------------------------------------
# severity_counts
# ---------------------------------------------------------------------------

def test_severity_counts_empty():
    assert severity_counts([]) == {"critical": 0, "warning": 0, "info": 0}


def test_severity_counts_mixed():
    opts = ClassifyOptions(critical_fields=frozenset({"price"}), warning_fields=frozenset({"name"}))
    changes = [
        _change("changed", ("1",), [_fc("price", "1", "2")]),
        _change("changed", ("2",), [_fc("name", "A", "B")]),
        _change("added", ("3",)),
    ]
    classified = classify_diff(make_result(*changes), opts)
    counts = severity_counts(classified)
    assert counts["critical"] == 1
    assert counts["warning"] == 1
    assert counts["info"] == 1
