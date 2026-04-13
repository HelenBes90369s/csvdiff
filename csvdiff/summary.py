"""Summary statistics for CSV diff results."""

from dataclasses import dataclass
from typing import List

from csvdiff.differ import DiffResult


@dataclass
class DiffSummary:
    """High-level summary of differences between two CSV files."""
    total_rows_left: int
    total_rows_right: int
    added: int
    removed: int
    changed: int
    unchanged: int

    @property
    def has_changes(self) -> bool:
        return self.added > 0 or self.removed > 0 or self.changed > 0

    @property
    def change_rate(self) -> float:
        """Fraction of left-side rows that were modified or removed."""
        if self.total_rows_left == 0:
            return 0.0
        return (self.removed + self.changed) / self.total_rows_left


def summarize(result: DiffResult, rows_left: int, rows_right: int) -> DiffSummary:
    """Compute a DiffSummary from a DiffResult and original row counts."""
    added = len(result.added)
    removed = len(result.removed)
    changed = len(result.changed)
    unchanged = rows_left - removed - changed
    return DiffSummary(
        total_rows_left=rows_left,
        total_rows_right=rows_right,
        added=added,
        removed=removed,
        changed=changed,
        unchanged=max(unchanged, 0),
    )


def format_summary(summary: DiffSummary) -> str:
    """Return a human-readable summary string."""
    lines: List[str] = [
        f"Rows (left):  {summary.total_rows_left}",
        f"Rows (right): {summary.total_rows_right}",
        f"  Added:      {summary.added}",
        f"  Removed:    {summary.removed}",
        f"  Changed:    {summary.changed}",
        f"  Unchanged:  {summary.unchanged}",
        f"Change rate:  {summary.change_rate:.1%}",
    ]
    return "\n".join(lines)
