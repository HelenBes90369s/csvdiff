"""Partition a DiffResult into multiple buckets based on a row field value."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


class PartitionError(Exception):
    """Raised when partitioning cannot be completed."""


@dataclass
class PartitionOptions:
    column: str
    include_unmatched: bool = True
    unmatched_key: str = "__other__"

    def __post_init__(self) -> None:
        if not self.column or not self.column.strip():
            raise PartitionError("column must be a non-empty string")
        if not self.unmatched_key or not self.unmatched_key.strip():
            raise PartitionError("unmatched_key must be a non-empty string")


@dataclass
class PartitionResult:
    buckets: Dict[str, DiffResult] = field(default_factory=dict)

    def keys(self) -> List[str]:
        return list(self.buckets.keys())

    def get(self, key: str) -> Optional[DiffResult]:
        return self.buckets.get(key)


def _pick_value(change: RowChange, column: str) -> Optional[str]:
    """Return the column value from whichever row snapshot is available."""
    row = change.new_row if change.new_row is not None else change.old_row
    if row is None:
        return None
    return row.get(column)


def _empty_result(source: DiffResult) -> DiffResult:
    return DiffResult(
        added=[], removed=[], changed=[],
        headers=source.headers, key_columns=source.key_columns
    )


def partition_diff(result: DiffResult, opts: PartitionOptions) -> PartitionResult:
    """Split *result* into per-value buckets keyed by *opts.column*."""
    buckets: Dict[str, DiffResult] = {}

    all_changes: List[RowChange] = (
        list(result.added) + list(result.removed) + list(result.changed)
    )

    for change in all_changes:
        value = _pick_value(change, opts.column)
        if value is None:
            if not opts.include_unmatched:
                continue
            key = opts.unmatched_key
        else:
            key = value

        if key not in buckets:
            buckets[key] = _empty_result(result)

        bucket = buckets[key]
        if change in result.added:
            bucket.added.append(change)  # type: ignore[attr-defined]
        elif change in result.removed:
            bucket.removed.append(change)  # type: ignore[attr-defined]
        else:
            bucket.changed.append(change)  # type: ignore[attr-defined]

    return PartitionResult(buckets=buckets)
