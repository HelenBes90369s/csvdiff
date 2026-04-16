"""Pivot a DiffResult so changes are indexed by field name.

Useful for answering questions like "which fields changed most often?"
or producing per-field change reports.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from csvdiff.differ import DiffResult, RowChange, FieldChange


class PivotError(ValueError):
    """Raised when pivoting cannot be completed."""


@dataclass
class FieldPivot:
    """All changes recorded for a single field name."""

    field_name: str
    changes: List[Tuple[str, FieldChange]] = field(default_factory=list)
    """List of (row_key_repr, FieldChange) pairs."""

    @property
    def count(self) -> int:
        return len(self.changes)

    @property
    def old_values(self) -> List[str]:
        return [fc.old_value for _, fc in self.changes]

    @property
    def new_values(self) -> List[str]:
        return [fc.new_value for _, fc in self.changes]

    @property
    def unique_row_keys(self) -> List[str]:
        """Return deduplicated row keys that have a change for this field."""
        seen = set()
        result = []
        for key, _ in self.changes:
            if key not in seen:
                seen.add(key)
                result.append(key)
        return result


def pivot_diff(result: DiffResult) -> Dict[str, FieldPivot]:
    """Return a mapping of field_name -> FieldPivot for all changed rows.

    Added and removed rows are skipped because they do not carry
    per-field FieldChange objects — only *changed* rows are pivoted.

    Args:
        result: A DiffResult produced by csvdiff.differ.

    Returns:
        Dictionary keyed by field name, values are FieldPivot instances.

    Raises:
        PivotError: If result is None.
    """
    if result is None:
        raise PivotError("result must not be None")

    pivots: Dict[str, FieldPivot] = {}

    for row_change in result.changed:
        key_repr = _key_repr(row_change)
        for fc in row_change.field_changes:
            if fc.field_name not in pivots:
                pivots[fc.field_name] = FieldPivot(field_name=fc.field_name)
            pivots[fc.field_name].changes.append((key_repr, fc))

    return pivots


def sorted_pivots(result: DiffResult, *, descending: bool = True) -> List[FieldPivot]:
    """Return FieldPivot list sorted by change frequency.

    Args:
        result: A DiffResult to pivot.
        descending: If True (default), most-changed fields come first.

    Returns:
        Sorted list of FieldPivot objects.
    """
    mapping = pivot_diff(result)
    return sorted(mapping.values(), key=lambda p: p.count, reverse=descending)


def _key_repr(row_change: RowChange) -> str:
    key = row_change.key
    if isinstance(key, tuple):
        return "|".join(str(k) for k in key)
    return str(key)
