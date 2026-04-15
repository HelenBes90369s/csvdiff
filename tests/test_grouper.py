"""Tests for csvdiff.grouper."""

import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.grouper import (
    DiffGroup,
    GroupError,
    group_by_field_value,
    group_by_kind,
)


def _fc(f: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=f, old_value=old, new_value=new)


def _change(
    key,
    old: dict | None = None,
    new: dict | None = None,
    fcs=None,
) -> RowChange:
    return RowChange(
        row_key=key,
        old=old,
        new=new,
        field_changes=fcs or [],
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
# group_by_kind
# ---------------------------------------------------------------------------

def test_group_by_kind_empty():
    result = make_result()
    groups = group_by_kind(result)
    assert set(groups.keys()) == {"added", "removed", "changed"}
    assert all(g.total == 0 for g in groups.values())


def test_group_by_kind_added_row():
    change = _change(("1",), new={"id": "1", "name": "Alice"})
    result = make_result(added=[change])
    groups = group_by_kind(result)
    assert groups["added"].total == 1
    assert groups["removed"].total == 0
    assert groups["changed"].total == 0


def test_group_by_kind_removed_row():
    change = _change(("2",), old={"id": "2", "name": "Bob"})
    result = make_result(removed=[change])
    groups = group_by_kind(result)
    assert groups["removed"].total == 1


def test_group_by_kind_changed_row():
    change = _change(
        ("3",),
        old={"id": "3", "val": "x"},
        new={"id": "3", "val": "y"},
        fcs=[_fc("val", "x", "y")],
    )
    result = make_result(changed=[change])
    groups = group_by_kind(result)
    assert groups["changed"].total == 1
    assert groups["changed"].changed[0].row_key == ("3",)


def test_group_by_kind_mixed():
    result = make_result(
        added=[_change(("a",), new={"id": "a"})],
        removed=[_change(("b",), old={"id": "b"})],
        changed=[_change(("c",), old={"id": "c", "v": "1"}, new={"id": "c", "v": "2"})],
    )
    groups = group_by_kind(result)
    assert groups["added"].total == 1
    assert groups["removed"].total == 1
    assert groups["changed"].total == 1


# ---------------------------------------------------------------------------
# group_by_field_value
# ---------------------------------------------------------------------------

def test_group_by_field_value_basic():
    c1 = _change(("1",), new={"id": "1", "dept": "eng"})
    c2 = _change(("2",), new={"id": "2", "dept": "hr"})
    c3 = _change(("3",), new={"id": "3", "dept": "eng"})
    result = make_result(added=[c1, c2, c3])
    groups = group_by_field_value(result, "dept")
    assert set(groups.keys()) == {"eng", "hr"}
    assert groups["eng"].total == 2
    assert groups["hr"].total == 1


def test_group_by_field_value_empty_column_raises():
    with pytest.raises(GroupError):
        group_by_field_value(make_result(), "")


def test_group_by_field_value_missing_column_raises():
    change = _change(("1",), new={"id": "1"})
    result = make_result(added=[change])
    with pytest.raises(GroupError, match="dept"):
        group_by_field_value(result, "dept")


def test_group_by_field_value_removed_uses_old_row():
    change = _change(("5",), old={"id": "5", "region": "west"})
    result = make_result(removed=[change])
    groups = group_by_field_value(result, "region")
    assert "west" in groups
    assert groups["west"].removed[0].row_key == ("5",)
