"""Group diff results by a field or change kind for aggregated reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


class GroupError(Exception):
    """Raised when grouping cannot be performed."""


@dataclass
class DiffGroup:
    key: str
    added: List[RowChange] = field(default_factory=list)
    removed: List[RowChange] = field(default_factory=list)
    changed: List[RowChange] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.added) + len(self.removed) + len(self.changed)


def _kind_key(change: RowChange) -> str:
    if change.old is None:
        return "added"
    if change.new is None:
        return "removed"
    return "changed"


def _field_key(column: str) -> Callable[[RowChange], List[str]]:
    def _key(change: RowChange) -> List[str]:
        keys: List[str] = []
        for fc in change.field_changes:
            if fc.field == column:
                keys.append(fc.new_value if change.new else fc.old_value)
        row = change.new or change.old or {}
        if not keys and column in row:
            keys.append(row[column])
        return keys if keys else [""]
    return _key


def group_by_kind(result: DiffResult) -> Dict[str, DiffGroup]:
    """Group all changes by their kind: added, removed, changed."""
    groups: Dict[str, DiffGroup] = {
        "added": DiffGroup(key="added"),
        "removed": DiffGroup(key="removed"),
        "changed": DiffGroup(key="changed"),
    }
    for change in result.added:
        groups["added"].added.append(change)
    for change in result.removed:
        groups["removed"].removed.append(change)
    for change in result.changed:
        groups["changed"].changed.append(change)
    return groups


def group_by_field_value(result: DiffResult, column: str) -> Dict[str, DiffGroup]:
    """Group all changes by the value of *column* in the new (or old) row."""
    if not column:
        raise GroupError("column name must not be empty")

    groups: Dict[str, DiffGroup] = {}

    def _get_or_create(val: str) -> DiffGroup:
        if val not in groups:
            groups[val] = DiffGroup(key=val)
        return groups[val]

    all_changes = [
        ("added", result.added),
        ("removed", result.removed),
        ("changed", result.changed),
    ]
    for kind, changes in all_changes:
        for change in changes:
            row = change.new or change.old or {}
            if column not in row:
                raise GroupError(
                    f"column '{column}' not found in row with key {change.row_key!r}"
                )
            val = row[column]
            grp = _get_or_create(val)
            getattr(grp, kind).append(change)

    return groups
