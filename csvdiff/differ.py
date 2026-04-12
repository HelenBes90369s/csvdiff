"""Core diffing logic for csvdiff."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from csvdiff.parser import Row, index_rows


ChangeKind = Literal["added", "removed", "modified"]


@dataclass
class RowChange:
    """Represents a single row-level change between two CSV files."""

    kind: ChangeKind
    key: tuple[str, ...]
    old: Row | None = None
    new: Row | None = None
    diff: dict[str, tuple[str, str]] = field(default_factory=dict)


@dataclass
class DiffResult:
    """Aggregated diff result between two CSV files."""

    added: list[RowChange] = field(default_factory=list)
    removed: list[RowChange] = field(default_factory=list)
    modified: list[RowChange] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    @property
    def total(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)


def diff_csv(
    old_rows: list[Row],
    new_rows: list[Row],
    key_columns: list[str],
) -> DiffResult:
    """Compute the diff between two lists of CSV rows.

    Args:
        old_rows: Rows from the original CSV.
        new_rows: Rows from the new CSV.
        key_columns: Columns used as the composite primary key.

    Returns:
        A DiffResult containing added, removed, and modified changes.
    """
    old_index = index_rows(old_rows, key_columns)
    new_index = index_rows(new_rows, key_columns)

    result = DiffResult()

    old_keys = set(old_index.keys())
    new_keys = set(new_index.keys())

    for key in sorted(new_keys - old_keys):
        result.added.append(RowChange(kind="added", key=key, new=new_index[key]))

    for key in sorted(old_keys - new_keys):
        result.removed.append(RowChange(kind="removed", key=key, old=old_index[key]))

    for key in sorted(old_keys & new_keys):
        old_row = old_index[key]
        new_row = new_index[key]
        field_diff = {
            col: (old_row[col], new_row[col])
            for col in old_row
            if col in new_row and old_row[col] != new_row[col]
        }
        if field_diff:
            result.modified.append(
                RowChange(kind="modified", key=key, old=old_row, new=new_row, diff=field_diff)
            )

    return result
