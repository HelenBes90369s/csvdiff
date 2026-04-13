"""Tests for csvdiff.sorter."""

import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.sorter import SortError, sort_diff, sort_keys


def make_change(key, change_type="changed", before=None, after=None):
    return RowChange(
        key=key,
        change_type=change_type,
        before=before or {},
        after=after or {},
        fields_changed=[],
    )


def make_result(changes):
    added = {c.key: c.after for c in changes if c.change_type == "added"}
    removed = {c.key: c.before for c in changes if c.change_type == "removed"}
    return DiffResult(changes=changes, added=added, removed=removed)


# ---------------------------------------------------------------------------
# sort_diff — by key
# ---------------------------------------------------------------------------

def test_sort_diff_by_key_ascending():
    changes = [
        make_change("charlie"),
        make_change("alpha"),
        make_change("bravo"),
    ]
    result = sort_diff(make_result(changes), by="key")
    assert [c.key for c in result.changes] == ["alpha", "bravo", "charlie"]


def test_sort_diff_by_key_descending():
    changes = [
        make_change("alpha"),
        make_change("charlie"),
        make_change("bravo"),
    ]
    result = sort_diff(make_result(changes), by="key", reverse=True)
    assert [c.key for c in result.changes] == ["charlie", "bravo", "alpha"]


def test_sort_diff_by_key_tuple_keys():
    changes = [
        make_change(("z", "1")),
        make_change(("a", "2")),
        make_change(("a", "1")),
    ]
    result = sort_diff(make_result(changes), by="key")
    assert result.changes[0].key == ("a", "1")
    assert result.changes[1].key == ("a", "2")
    assert result.changes[2].key == ("z", "1")


# ---------------------------------------------------------------------------
# sort_diff — by change_type
# ---------------------------------------------------------------------------

def test_sort_diff_by_change_type():
    changes = [
        make_change("x", change_type="removed"),
        make_change("y", change_type="added"),
        make_change("z", change_type="changed"),
    ]
    result = sort_diff(make_result(changes), by="change_type")
    types = [c.change_type for c in result.changes]
    assert types == sorted(types)


# ---------------------------------------------------------------------------
# sort_diff — preserves added/removed mappings
# ---------------------------------------------------------------------------

def test_sort_diff_preserves_added_removed():
    changes = [
        make_change("b", change_type="added", after={"v": "2"}),
        make_change("a", change_type="removed", before={"v": "1"}),
    ]
    original = make_result(changes)
    result = sort_diff(original, by="key")
    assert result.added == original.added
    assert result.removed == original.removed


# ---------------------------------------------------------------------------
# sort_diff — invalid field
# ---------------------------------------------------------------------------

def test_sort_diff_invalid_field_raises():
    with pytest.raises(SortError, match="Invalid sort field"):
        sort_diff(make_result([]), by="nonexistent")


# ---------------------------------------------------------------------------
# sort_keys
# ---------------------------------------------------------------------------

def test_sort_keys_scalars():
    assert sort_keys(["c", "a", "b"]) == ["a", "b", "c"]


def test_sort_keys_tuples():
    keys = [("b", "1"), ("a", "2"), ("a", "1")]
    assert sort_keys(keys) == [("a", "1"), ("a", "2"), ("b", "1")]


def test_sort_keys_reverse():
    assert sort_keys(["a", "c", "b"], reverse=True) == ["c", "b", "a"]
