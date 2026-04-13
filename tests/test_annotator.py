"""Tests for csvdiff.annotator."""
from __future__ import annotations

from typing import Optional

import pytest

from csvdiff.annotator import (
    Annotation,
    AnnotatedRow,
    AnnotationError,
    annotate_diff,
    group_by_annotation,
)
from csvdiff.differ import DiffResult, FieldChange, RowChange


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(kind: str, key: tuple, **kwargs) -> RowChange:
    return RowChange(
        kind=kind,
        key=key,
        old_row=kwargs.get("old_row", {}),
        new_row=kwargs.get("new_row", {}),
        field_changes=kwargs.get("field_changes", []),
    )


def make_result(
    added=None, removed=None, changed=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_annotate_empty_result_returns_empty_list():
    result = make_result()
    rows = annotate_diff(result)
    assert rows == []


def test_annotate_includes_kind_by_default():
    change = _change("added", ("1",), new_row={"id": "1"})
    result = make_result(added=[change])
    rows = annotate_diff(result)
    assert len(rows) == 1
    assert rows[0].get("kind") == "added"


def test_annotate_kind_can_be_disabled():
    change = _change("removed", ("2",), old_row={"id": "2"})
    result = make_result(removed=[change])
    rows = annotate_diff(result, include_kind=False)
    assert rows[0].get("kind") is None


def test_annotate_custom_rule_applied():
    def severity_rule(change: RowChange) -> Optional[Annotation]:
        if change.kind == "removed":
            return Annotation(key="severity", value="high")
        return Annotation(key="severity", value="low")

    added = _change("added", ("1",))
    removed = _change("removed", ("2",))
    result = make_result(added=[added], removed=[removed])
    rows = annotate_diff(result, rules=[severity_rule])

    by_kind = {r.change.kind: r for r in rows}
    assert by_kind["added"].get("severity") == "low"
    assert by_kind["removed"].get("severity") == "high"


def test_annotate_multiple_rules_all_applied():
    rule_a = lambda c: Annotation(key="a", value="1")
    rule_b = lambda c: Annotation(key="b", value="2")
    change = _change("changed", ("3",), field_changes=[_fc("name", "x", "y")])
    result = make_result(changed=[change])
    rows = annotate_diff(result, rules=[rule_a, rule_b])
    assert rows[0].get("a") == "1"
    assert rows[0].get("b") == "2"


def test_annotate_rule_returning_none_is_skipped():
    rule = lambda c: None
    change = _change("added", ("1",))
    result = make_result(added=[change])
    rows = annotate_diff(result, rules=[rule])
    # Only the built-in kind annotation should be present
    assert len(rows[0].annotations) == 1


def test_group_by_annotation_basic():
    added = _change("added", ("1",))
    removed = _change("removed", ("2",))
    result = make_result(added=[added], removed=[removed])
    rows = annotate_diff(result)
    groups = group_by_annotation(rows, "kind")
    assert set(groups.keys()) == {"added", "removed"}
    assert len(groups["added"]) == 1
    assert len(groups["removed"]) == 1


def test_group_by_annotation_missing_key_goes_to_unset():
    change = _change("added", ("1",))
    result = make_result(added=[change])
    rows = annotate_diff(result, include_kind=False)
    groups = group_by_annotation(rows, "nonexistent")
    assert "__unset__" in groups
    assert len(groups["__unset__"]) == 1


def test_annotated_row_get_returns_none_for_missing_key():
    change = _change("added", ("1",))
    row = AnnotatedRow(change=change, annotations=[])
    assert row.get("missing") is None
