"""Tests for csvdiff.aligner."""
import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.aligner import (
    AlignError,
    AlignedPair,
    align_diff,
    aligned_keys,
    split_aligned,
)


def _fc(field="col", old="a", new="b"):
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key, kind="changed"):
    return RowChange(
        key=key,
        kind=kind,
        old_row={"id": key} if kind != "added" else {},
        new_row={"id": key} if kind != "removed" else {},
        field_changes=[_fc()] if kind == "changed" else [],
    )


def make_result(changes):
    return DiffResult(changes=changes, headers=["id", "col"])


def test_align_none_raises():
    with pytest.raises(AlignError):
        align_diff(None, make_result([]))


def test_align_both_empty_returns_empty():
    result = align_diff(make_result([]), make_result([]))
    assert result == []


def test_align_shared_key():
    left = make_result([_change("1")])
    right = make_result([_change("1")])
    pairs = align_diff(left, right)
    assert len(pairs) == 1
    assert pairs[0].key == ("1",)
    assert pairs[0].left is not None
    assert pairs[0].right is not None


def test_align_fill_missing_true_includes_all():
    left = make_result([_change("1"), _change("2")])
    right = make_result([_change("2"), _change("3")])
    pairs = align_diff(left, right, fill_missing=True)
    keys = aligned_keys(pairs)
    assert ("1",) in keys
    assert ("2",) in keys
    assert ("3",) in keys
    assert len(pairs) == 3


def test_align_fill_missing_false_intersection_only():
    left = make_result([_change("1"), _change("2")])
    right = make_result([_change("2"), _change("3")])
    pairs = align_diff(left, right, fill_missing=False)
    keys = aligned_keys(pairs)
    assert keys == [("2",)]


def test_aligned_keys_order_is_sorted():
    left = make_result([_change("z"), _change("a")])
    right = make_result([_change("m")])
    pairs = align_diff(left, right)
    keys = aligned_keys(pairs)
    assert keys == sorted(keys)


def test_split_aligned_groups_correctly():
    left = make_result([_change("1"), _change("2")])
    right = make_result([_change("2"), _change("3")])
    pairs = align_diff(left, right, fill_missing=True)
    both, left_only, right_only = split_aligned(pairs)
    assert len(both) == 1
    assert both[0].key == ("2",)
    assert len(left_only) == 1
    assert left_only[0].key == ("1",)
    assert len(right_only) == 1
    assert right_only[0].key == ("3",)


def test_align_tuple_key():
    c = _change(("a", "b"))
    left = make_result([c])
    right = make_result([c])
    pairs = align_diff(left, right)
    assert pairs[0].key == ("a", "b")
