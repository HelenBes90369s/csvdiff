"""Tests for csvdiff.ranker."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.ranker import RankError, RankOptions, rank_diff, top_n


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fc(field: str, old: str = "a", new: str = "b") -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key, *fields: str, kind: str = "changed") -> RowChange:
    changes = [_fc(f) for f in fields]
    row = {"id": str(key)}
    if kind == "added":
        return RowChange(key=(str(key),), old_row=None, new_row=row, changes=changes)
    if kind == "removed":
        return RowChange(key=(str(key),), old_row=row, new_row=None, changes=changes)
    return RowChange(key=(str(key),), old_row=row, new_row={**row, "x": "y"}, changes=changes)


def make_result(
    added=None, removed=None, changed=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


# ---------------------------------------------------------------------------
# RankOptions validation
# ---------------------------------------------------------------------------

def test_rank_options_default_is_valid():
    opts = RankOptions()
    assert opts.by == "changes"
    assert opts.descending is True


def test_rank_options_invalid_by_raises():
    with pytest.raises(RankError, match="Invalid 'by'"):
        RankOptions(by="nonsense")


# ---------------------------------------------------------------------------
# rank_diff
# ---------------------------------------------------------------------------

def test_rank_diff_empty_result():
    result = make_result()
    ranked = rank_diff(result)
    assert ranked == []


def test_rank_diff_by_changes_descending():
    c1 = _change(1, "a")           # 1 change
    c2 = _change(2, "a", "b", "c") # 3 changes
    c3 = _change(3, "a", "b")      # 2 changes
    result = make_result(changed=[c1, c2, c3])
    ranked = rank_diff(result)
    assert ranked[0] is c2
    assert ranked[1] is c3
    assert ranked[2] is c1


def test_rank_diff_by_changes_ascending():
    c1 = _change(1, "a")
    c2 = _change(2, "a", "b", "c")
    result = make_result(changed=[c1, c2])
    opts = RankOptions(descending=False)
    ranked = rank_diff(result, opts)
    assert ranked[0] is c1
    assert ranked[1] is c2


def test_rank_diff_includes_added_and_removed():
    added = _change("A", kind="added")
    removed = _change("R", kind="removed")
    changed = _change("C", "f1")
    result = make_result(added=[added], removed=[removed], changed=[changed])
    ranked = rank_diff(result)
    keys = {r.key for r in ranked}
    assert ("A",) in keys
    assert ("R",) in keys
    assert ("C",) in keys


def test_rank_diff_by_key():
    c1 = _change("zebra")
    c2 = _change("apple")
    result = make_result(changed=[c1, c2])
    opts = RankOptions(by="key", descending=False)
    ranked = rank_diff(result, opts)
    assert ranked[0].key == ("apple",)
    assert ranked[1].key == ("zebra",)


def test_rank_diff_by_specific_field():
    c1 = _change(1, "price", "name")   # price changed
    c2 = _change(2, "name")             # price NOT changed
    result = make_result(changed=[c1, c2])
    opts = RankOptions(field="price")
    ranked = rank_diff(result, opts)
    assert ranked[0] is c1   # has price change
    assert ranked[1] is c2   # no price change


# ---------------------------------------------------------------------------
# top_n
# ---------------------------------------------------------------------------

def test_top_n_returns_correct_count():
    changes = [_change(i, "f") for i in range(5)]
    result = make_result(changed=changes)
    assert len(top_n(result, 3)) == 3


def test_top_n_zero_returns_empty():
    changes = [_change(i, "f") for i in range(5)]
    result = make_result(changed=changes)
    assert top_n(result, 0) == []


def test_top_n_negative_raises():
    result = make_result()
    with pytest.raises(RankError, match="non-negative"):
        top_n(result, -1)


def test_top_n_larger_than_result_returns_all():
    changes = [_change(i, "f") for i in range(3)]
    result = make_result(changed=changes)
    assert len(top_n(result, 100)) == 3
