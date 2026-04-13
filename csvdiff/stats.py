"""Compute statistical metrics from a DiffResult."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from csvdiff.differ import DiffResult


@dataclass
class DiffStats:
    total_added: int
    total_removed: int
    total_changed: int
    total_unchanged: int
    total_rows: int
    changed_fields: Dict[str, int]  # field name -> number of times it changed

    @property
    def change_ratio(self) -> float:
        """Fraction of rows that have any change (0.0 – 1.0)."""
        if self.total_rows == 0:
            return 0.0
        return (self.total_added + self.total_removed + self.total_changed) / self.total_rows

    @property
    def most_changed_fields(self) -> List[str]:
        """Field names sorted by change frequency, descending."""
        return sorted(self.changed_fields, key=lambda f: self.changed_fields[f], reverse=True)


def compute_stats(result: DiffResult) -> DiffStats:
    """Return a :class:`DiffStats` computed from *result*."""
    field_counts: Dict[str, int] = {}

    for change in result.changed:
        for field_change in change.field_changes:
            field_counts[field_change.field] = field_counts.get(field_change.field, 0) + 1

    total_added = len(result.added)
    total_removed = len(result.removed)
    total_changed = len(result.changed)
    # unchanged is everything else; DiffResult carries the original row count
    total_rows = getattr(result, "total_rows", total_added + total_removed + total_changed)
    total_unchanged = max(0, total_rows - total_added - total_removed - total_changed)

    return DiffStats(
        total_added=total_added,
        total_removed=total_removed,
        total_changed=total_changed,
        total_unchanged=total_unchanged,
        total_rows=total_rows,
        changed_fields=field_counts,
    )


def format_stats(stats: DiffStats) -> str:
    """Return a human-readable summary string for *stats*."""
    lines = [
        f"Rows total   : {stats.total_rows}",
        f"  Added      : {stats.total_added}",
        f"  Removed    : {stats.total_removed}",
        f"  Changed    : {stats.total_changed}",
        f"  Unchanged  : {stats.total_unchanged}",
        f"Change ratio : {stats.change_ratio:.1%}",
    ]
    if stats.most_changed_fields:
        top = ", ".join(
            f"{f}({stats.changed_fields[f]})" for f in stats.most_changed_fields[:5]
        )
        lines.append(f"Top fields   : {top}")
    return "\n".join(lines)
