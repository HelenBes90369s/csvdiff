"""Tests for csvdiff.pruner."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.pruner import PruneError, PruneOptions, prune_diff


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key: tuple, kind: str = "changed", fields=()) -> RowChange:
    return RowChange(
        key=key,
        kind=kind,
        old_row={},
        new_row={},
        field_changes=list(fields),
    )


def make_result(*changes: RowChange) -> DiffResult:
    return DiffResult(added=[], removed=[], changes=list(changes))


# --- option validation ---

def test_options_non_callable_raises():
    with pytest.raises(PruneError):
        PruneOptions(predicate="not_callable")  # type: ignore


# --- none guards ---

def test_prune_none_result_raises():
    opts = PruneOptions(predicate=lambda c: True)
    with pytest.raises(PruneError):
        prune_diff(None, opts)


def test_prune_none_options_raises():
    with pytest.raises(PruneError):
        prune_diff(make_result(), None)  # type: ignore


# --- basic pruning ---

def test_prune_empty_result_returns_empty():
    opts = PruneOptions(predicate=lambda c: True)
    pr = prune_diff(make_result(), opts)
    assert pr.pruned_count == 0
    assert pr.result.changes == []


def test_prune_removes_matching_rows():
    c1 = _change(("A",), fields=[_fc("x", "1", "2")])
    c2 = _change(("B",), fields=[_fc("y", "3", "4")])
    opts = PruneOptions(predicate=lambda c: c.key == ("A",))
    pr = prune_diff(make_result(c1, c2), opts)
    assert pr.pruned_count == 1
    assert pr.result.changes == [c2]


def test_prune_keeps_all_when_predicate_false():
    c1 = _change(("A",))
    c2 = _change(("B",))
    opts = PruneOptions(predicate=lambda c: False)
    pr = prune_diff(make_result(c1, c2), opts)
    assert pr.pruned_count == 0
    assert len(pr.result.changes) == 2


def test_prune_removes_all_when_predicate_true():
    changes = [_change((str(i),)) for i in range(5)]
    opts = PruneOptions(predicate=lambda c: True)
    pr = prune_diff(make_result(*changes), opts)
    assert pr.pruned_count == 5
    assert pr.result.changes == []


# --- invert flag ---

def test_prune_invert_keeps_only_matching():
    c1 = _change(("keep",))
    c2 = _change(("drop",))
    opts = PruneOptions(predicate=lambda c: c.key == ("keep",), invert=True)
    pr = prune_diff(make_result(c1, c2), opts)
    # invert=True means matching rows are KEPT
    assert pr.result.changes == [c1]
    assert pr.pruned_count == 1


# --- added/removed preserved ---

def test_prune_preserves_added_and_removed():
    result = DiffResult(
        added=[{"id": "1"}],
        removed=[{"id": "2"}],
        changes=[_change(("3",))],
    )
    opts = PruneOptions(predicate=lambda c: True)
    pr = prune_diff(result, opts)
    assert pr.result.added == [{"id": "1"}]
    assert pr.result.removed == [{"id": "2"}]
