"""splitter.py — Split a DiffResult into multiple DiffResults by a row field value."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


class SplitError(Exception):
    """Raised when splitting fails."""


@dataclass
class SplitOptions:
    column: str
    include_unchanged: bool = False

    def __post_init__(self) -> None:
        if not self.column or not self.column.strip():
            raise SplitError("column must be a non-empty string")
        self.column = self.column.strip()


def _row_value(change: RowChange, column: str) -> Optional[str]:
    """Return the value of *column* from a RowChange, preferring the new row."""
    row = change.new_row if change.new_row is not None else change.old_row
    if row is None:
        return None
    return row.get(column)


def split_diff(result: DiffResult, options: SplitOptions) -> Dict[str, DiffResult]:
    """Partition *result* into separate DiffResults keyed by the value of *options.column*.

    Rows whose column value is ``None`` (i.e. the column is absent) are
    collected under the special key ``"__missing__"``.

    Returns:
        A dict mapping each distinct column value to a DiffResult that
        contains only the changes belonging to that bucket.
    """
    if result is None:
        raise SplitError("result must not be None")

    buckets: Dict[str, List[RowChange]] = {}

    for change in result.changes:
        key = _row_value(change, options.column)
        bucket_key = key if key is not None else "__missing__"
        buckets.setdefault(bucket_key, []).append(change)

    return {
        bucket_key: DiffResult(
            changes=changes,
            added_rows=result.added_rows if options.include_unchanged else [],
            removed_rows=result.removed_rows if options.include_unchanged else [],
        )
        for bucket_key, changes in buckets.items()
    }


def bucket_keys(result: DiffResult, options: SplitOptions) -> List[str]:
    """Return the sorted list of distinct bucket keys without building full DiffResults."""
    if result is None:
        raise SplitError("result must not be None")
    seen = set()
    for change in result.changes:
        val = _row_value(change, options.column)
        seen.add(val if val is not None else "__missing__")
    return sorted(seen)
