"""Tests for csvdiff.joiner."""
import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.joiner import JoinError, JoinOptions, join_diff


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key, kind="changed", fields=None) -> RowChange:
    return RowChange(key=key, kind=kind, field_changes=fields or [])


def make_result(*changes: RowChange) -> DiffResult:
    added = [c.key for c in changes if c.kind == "added"]
    removed = [c.key for c in changes if c.kind == "removed"]
    return DiffResult(added=added, removed=removed, changes=list(changes))


# ---------------------------------------------------------------------------
# JoinOptions
# ---------------------------------------------------------------------------

def test_join_options_default_is_union():
    assert JoinOptions().strategy == "union"


def test_join_options_invalid_raises():
    with pytest.raises(JoinError, match="Invalid strategy"):
        JoinOptions(strategy="outer")


# ---------------------------------------------------------------------------
# join_diff – guards
# ---------------------------------------------------------------------------

def test_join_diff_none_left_raises():
    r = make_result()
    with pytest.raises(JoinError):
        join_diff(None, r)


def test_join_diff_none_right_raises():
    r = make_result()
    with pytest.raises(JoinError):
        join_diff(r, None)


# ---------------------------------------------------------------------------
# union
# ---------------------------------------------------------------------------

def test_union_combines_disjoint_results():
    left = make_result(_change("a", "added"))
    right = make_result(_change("b", "removed"))
    result = join_diff(left, right)
    keys = {c.key for c in result.changes}
    assert keys == {"a", "b"}


def test_union_left_wins_on_conflict():
    left = make_result(_change("x", "added"))
    right = make_result(_change("x", "removed"))
    result = join_diff(left, right)
    assert len(result.changes) == 1
    assert result.changes[0].kind == "added"


# ---------------------------------------------------------------------------
# intersection
# ---------------------------------------------------------------------------

def test_intersection_keeps_shared_keys_only():
    left = make_result(_change("a"), _change("b"))
    right = make_result(_change("b"), _change("c"))
    result = join_diff(left, right, JoinOptions(strategy="intersection"))
    keys = {c.key for c in result.changes}
    assert keys == {"b"}


def test_intersection_empty_when_no_overlap():
    left = make_result(_change("a"))
    right = make_result(_change("b"))
    result = join_diff(left, right, JoinOptions(strategy="intersection"))
    assert result.changes == []


# ---------------------------------------------------------------------------
# left / right
# ---------------------------------------------------------------------------

def test_left_strategy_returns_only_left():
    left = make_result(_change("a"))
    right = make_result(_change("b"))
    result = join_diff(left, right, JoinOptions(strategy="left"))
    assert [c.key for c in result.changes] == ["a"]


def test_right_strategy_returns_only_right():
    left = make_result(_change("a"))
    right = make_result(_change("b"))
    result = join_diff(left, right, JoinOptions(strategy="right"))
    assert [c.key for c in result.changes] == ["b"]
