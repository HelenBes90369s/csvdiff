"""Tests for csvdiff.deduplicator."""

from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.deduplicator import (
    DeduplicateError,
    DeduplicateOptions,
    deduplicate_diff,
)


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key: tuple, kind: str, fields=None) -> RowChange:
    return RowChange(key=key, kind=kind, fields=fields or [], row={})


def make_result(changes) -> DiffResult:
    return DiffResult(added=[], removed=[], changes=changes)


# ---------------------------------------------------------------------------
# DeduplicateOptions validation
# ---------------------------------------------------------------------------

def test_options_default_is_first():
    opts = DeduplicateOptions()
    assert opts.keep == "first"


def test_options_last_is_valid():
    opts = DeduplicateOptions(keep="last")
    assert opts.keep == "last"


def test_options_invalid_keep_raises():
    with pytest.raises(DeduplicateError, match="keep must be"):
        DeduplicateOptions(keep="middle")


# ---------------------------------------------------------------------------
# deduplicate_diff – no duplicates
# ---------------------------------------------------------------------------

def test_deduplicate_empty_result():
    result = make_result([])
    out = deduplicate_diff(result)
    assert out.changes == []


def test_deduplicate_no_duplicates_unchanged():
    c1 = _change(("A",), "added")
    c2 = _change(("B",), "removed")
    result = make_result([c1, c2])
    out = deduplicate_diff(result)
    assert len(out.changes) == 2


# ---------------------------------------------------------------------------
# deduplicate_diff – with duplicates
# ---------------------------------------------------------------------------

def test_deduplicate_removes_exact_duplicate():
    c1 = _change(("A",), "added")
    c2 = _change(("A",), "added")  # exact duplicate
    result = make_result([c1, c2])
    out = deduplicate_diff(result)
    assert len(out.changes) == 1
    assert out.changes[0].key == ("A",)


def test_deduplicate_keeps_first_by_default():
    c1 = _change(("A",), "changed", [_fc("x", "1", "2")])
    c2 = _change(("A",), "changed", [_fc("x", "1", "2")])
    result = make_result([c1, c2])
    out = deduplicate_diff(result)
    assert len(out.changes) == 1
    assert out.changes[0] is c1


def test_deduplicate_keeps_last_when_specified():
    c1 = _change(("A",), "added")
    c2 = _change(("A",), "added")
    result = make_result([c1, c2])
    opts = DeduplicateOptions(keep="last")
    out = deduplicate_diff(result, options=opts)
    assert len(out.changes) == 1
    assert out.changes[0] is c2


def test_deduplicate_different_field_changes_kept_separate():
    c1 = _change(("A",), "changed", [_fc("x", "1", "2")])
    c2 = _change(("A",), "changed", [_fc("x", "1", "3")])  # different mutation
    result = make_result([c1, c2])
    out = deduplicate_diff(result)
    assert len(out.changes) == 2


def test_deduplicate_preserves_added_and_removed():
    """Deduplication of changes must not affect the added/removed lists."""
    added = [_change(("X",), "added")]
    removed = [_change(("Y",), "removed")]
    c1 = _change(("A",), "changed", [_fc("x", "1", "2")])
    c2 = _change(("A",), "changed", [_fc("x", "1", "2")])
    result = DiffResult(added=added, removed=removed, changes=[c1, c2])
    out = deduplicate_diff(result)
    assert out.added == added
    assert out.removed == removed
    assert len(out.changes) == 1
