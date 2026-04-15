"""Tests for csvdiff.partitioner."""

import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.partitioner import (
    PartitionError,
    PartitionOptions,
    PartitionResult,
    partition_diff,
)


HEADERS = ["id", "region", "value"]
KEYS = ["id"]


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(
    kind: str,
    row_id: str,
    region: str = "east",
    old_row=None,
    new_row=None,
    changes=None,
) -> RowChange:
    base = {"id": row_id, "region": region, "value": "1"}
    if kind == "added":
        return RowChange(key=(row_id,), old_row=None, new_row={**base})
    if kind == "removed":
        return RowChange(key=(row_id,), old_row={**base}, new_row=None)
    return RowChange(
        key=(row_id,),
        old_row={**base, "value": "0"},
        new_row={**base},
        changes=changes or [_fc("value", "0", "1")],
    )


def make_result(added=None, removed=None, changed=None) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
        headers=HEADERS,
        key_columns=KEYS,
    )


# --- PartitionOptions validation ---

def test_options_empty_column_raises():
    with pytest.raises(PartitionError):
        PartitionOptions(column="")


def test_options_whitespace_column_raises():
    with pytest.raises(PartitionError):
        PartitionOptions(column="   ")


def test_options_empty_unmatched_key_raises():
    with pytest.raises(PartitionError):
        PartitionOptions(column="region", unmatched_key="")


def test_options_defaults_are_valid():
    opts = PartitionOptions(column="region")
    assert opts.include_unmatched is True
    assert opts.unmatched_key == "__other__"


# --- partition_diff ---

def test_partition_empty_result_returns_empty_buckets():
    result = make_result()
    pr = partition_diff(result, PartitionOptions(column="region"))
    assert pr.buckets == {}


def test_partition_added_rows_by_region():
    result = make_result(
        added=[_change("added", "1", "east"), _change("added", "2", "west")]
    )
    pr = partition_diff(result, PartitionOptions(column="region"))
    assert set(pr.keys()) == {"east", "west"}
    assert len(pr.get("east").added) == 1
    assert len(pr.get("west").added) == 1


def test_partition_multiple_kinds_same_bucket():
    result = make_result(
        added=[_change("added", "1", "east")],
        removed=[_change("removed", "2", "east")],
        changed=[_change("changed", "3", "east")],
    )
    pr = partition_diff(result, PartitionOptions(column="region"))
    bucket = pr.get("east")
    assert len(bucket.added) == 1
    assert len(bucket.removed) == 1
    assert len(bucket.changed) == 1


def test_partition_preserves_headers_and_keys():
    result = make_result(added=[_change("added", "1", "north")])
    pr = partition_diff(result, PartitionOptions(column="region"))
    bucket = pr.get("north")
    assert bucket.headers == HEADERS
    assert bucket.key_columns == KEYS


def test_partition_unmatched_goes_to_other_bucket():
    change = RowChange(key=("99",), old_row=None, new_row={"id": "99", "value": "x"})
    result = DiffResult(
        added=[change], removed=[], changed=[], headers=HEADERS, key_columns=KEYS
    )
    pr = partition_diff(result, PartitionOptions(column="region"))
    assert "__other__" in pr.keys()
    assert len(pr.get("__other__").added) == 1


def test_partition_exclude_unmatched():
    change = RowChange(key=("99",), old_row=None, new_row={"id": "99", "value": "x"})
    result = DiffResult(
        added=[change], removed=[], changed=[], headers=HEADERS, key_columns=KEYS
    )
    pr = partition_diff(
        result, PartitionOptions(column="region", include_unmatched=False)
    )
    assert pr.buckets == {}
