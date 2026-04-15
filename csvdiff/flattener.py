"""Flatten a DiffResult into a list of plain dicts for easy serialisation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from csvdiff.differ import DiffResult, RowChange


class FlattenError(Exception):
    """Raised when flattening fails."""


@dataclass(frozen=True)
class FlatRow:
    """A single flattened change record."""

    kind: str  # 'added' | 'removed' | 'changed'
    key: str
    field: str | None
    old_value: str | None
    new_value: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "key": self.key,
            "field": self.field,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }


def _row_key(change: RowChange) -> str:
    key = change.key
    if isinstance(key, tuple):
        return "|".join(str(k) for k in key)
    return str(key)


def flatten_diff(result: DiffResult) -> list[FlatRow]:
    """Return a flat list of FlatRow records from *result*.

    - Added rows produce one record per field with old_value=None.
    - Removed rows produce one record per field with new_value=None.
    - Changed rows produce one record per changed field.
    """
    if result is None:
        raise FlattenError("result must not be None")

    rows: list[FlatRow] = []

    for change in result.added:
        key_str = _row_key(change)
        for field, value in change.row.items():
            rows.append(FlatRow(kind="added", key=key_str, field=field,
                                old_value=None, new_value=value))

    for change in result.removed:
        key_str = _row_key(change)
        for field, value in change.row.items():
            rows.append(FlatRow(kind="removed", key=key_str, field=field,
                                old_value=value, new_value=None))

    for change in result.changed:
        key_str = _row_key(change)
        for fc in change.field_changes:
            rows.append(FlatRow(kind="changed", key=key_str, field=fc.field,
                                old_value=fc.old_value, new_value=fc.new_value))

    return rows
