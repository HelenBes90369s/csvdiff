"""Core diffing logic for csvdiff."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class RowChange:
    """Represents a single changed row."""
    key: str
    before: dict
    after: dict

    @property
    def changed_fields(self) -> List[str]:
        """Return list of field names that differ between before and after."""
        return [
            k for k in set(self.before) | set(self.after)
            if self.before.get(k) != self.after.get(k)
        ]


@dataclass
class DiffResult:
    """Holds the complete diff between two CSV files."""
    added: List[dict] = field(default_factory=list)
    removed: List[dict] = field(default_factory=list)
    changed: List[RowChange] = field(default_factory=list)


def has_changes(result: DiffResult) -> bool:
    """Return True if the diff contains any changes."""
    return bool(result.added or result.removed or result.changed)


def total(result: DiffResult) -> int:
    """Return total number of change entries."""
    return len(result.added) + len(result.removed) + len(result.changed)


def diff_csv(
    old_index: Dict[str, dict],
    new_index: Dict[str, dict],
) -> DiffResult:
    """Diff two indexed CSV datasets.

    Args:
        old_index: Mapping of key -> row dict for the old file.
        new_index: Mapping of key -> row dict for the new file.

    Returns:
        A DiffResult describing all additions, removals, and changes.
    """
    result = DiffResult()

    old_keys = set(old_index)
    new_keys = set(new_index)

    for key in sorted(new_keys - old_keys):
        result.added.append(new_index[key])

    for key in sorted(old_keys - new_keys):
        result.removed.append(old_index[key])

    for key in sorted(old_keys & new_keys):
        old_row = old_index[key]
        new_row = new_index[key]
        if old_row != new_row:
            result.changed.append(RowChange(key=key, before=old_row, after=new_row))

    return result
